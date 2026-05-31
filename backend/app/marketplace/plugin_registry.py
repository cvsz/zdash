"""DB-backed plugin registry.

Seeds built-in manifests on startup and provides CRUD operations
against the plugin_manifests table.
"""

from __future__ import annotations

from copy import deepcopy
from datetime import datetime
from typing import Any

from sqlalchemy import or_
from sqlalchemy.orm import Session

from .builtins import BUILTINS
from .models import PluginManifest, PluginStatus, manifest_to_dict


# ------------------------------------------------------------------ #
# Seed                                                                  #
# ------------------------------------------------------------------ #


def seed_builtins(db: Session) -> list[dict[str, Any]]:
    """Insert any built-in manifests not already present in the DB."""
    seeded: list[dict[str, Any]] = []
    for builtin in BUILTINS:
        slug = builtin.__dict__.get("slug", "")
        existing = (
            db.query(PluginManifest)
            .filter(PluginManifest.slug == slug)
            .first()
        )
        if existing is None:
            fresh = deepcopy(builtin)
            fresh.id = builtin.__dict__.get("id", "")
            db.add(fresh)
            db.flush()
            seeded.append(manifest_to_dict(fresh))
    if seeded:
        db.commit()
    return seeded


# ------------------------------------------------------------------ #
# Query helpers                                                         #
# ------------------------------------------------------------------ #


def _ensure_session(db: Session | None) -> tuple[Session, bool]:
    """Return (session, own) — auto-creates and seeds if db is None."""
    if db is not None:
        return db, False
    from app.db.session import SessionLocal
    sess = SessionLocal()
    seed_builtins(sess)
    return sess, True


def list_plugins(
    db: Session | None = None,
    search: str | None = None,
    category: str | None = None,
    status: str | None = None,
) -> list[PluginManifest]:
    """Return manifests matching optional filters, ordered by name.

    When called without *db* and without filters, returns the built-in
    list directly for backward compatibility (callers that expect the
    same Python objects as ``BUILTINS``).

    When *db* or any filter is provided, queries the database and
    returns DB-backed ORM instances.  API endpoints should convert
    with ``manifest_to_dict`` or ``model_dump`` when serialising.
    """
    if db is None and not search and not category and not status:
        return list(BUILTINS)

    sess, own = _ensure_session(db)
    try:
        q = sess.query(PluginManifest)

        if search:
            like = f"%{search}%"
            q = q.filter(
                or_(
                    PluginManifest.name.ilike(like),
                    PluginManifest.description.ilike(like),
                    PluginManifest.slug.ilike(like),
                )
            )
        if category:
            q = q.filter(PluginManifest.category == category)
        if status:
            q = q.filter(PluginManifest.status == status)

        q = q.order_by(PluginManifest.name)
        result = list(q.all())
        return result
    finally:
        if own:
            sess.expunge_all()
            sess.close()


def get_plugin(
    db: Session | None = None,
    plugin_id: str | None = None,
) -> PluginManifest | dict[str, Any] | None:
    """Fetch a single manifest by primary key.

    Accepts positional ``db`` or ``plugin_id`` for backward compatibility:
        get_plugin(db, plugin_id)   # new style
        get_plugin(plugin_id)       # old style (auto-session)

    Returns the ORM instance for callers that expect attribute access.
    The PK is eagerly loaded so ``.id`` remains accessible even when
    the object is detached.
    """
    if isinstance(db, str):
        plugin_id = db
        db = None
    sess, own = _ensure_session(db)
    try:
        m = sess.query(PluginManifest).filter(PluginManifest.id == plugin_id).first()
        return m
    finally:
        if own:
            sess.expunge_all()
            sess.close()


# ------------------------------------------------------------------ #
# Registration                                                          #
# ------------------------------------------------------------------ #


def register_plugin_manifest(
    db: Session,
    manifest: PluginManifest,
    actor: str,
) -> dict[str, Any]:
    """Insert or update a manifest in the DB.

    If a row with the same *slug* already exists its fields are
    overwritten (upsert-by-slug).  Audit metadata is set to the
    current timestamp regardless.
    """
    existing = (
        db.query(PluginManifest)
        .filter(PluginManifest.slug == manifest.__dict__.get("slug", ""))
        .first()
    )

    if existing:
        existing.name = manifest.name
        existing.version = manifest.version
        existing.description = manifest.description
        existing.author = manifest.author
        existing.category = manifest.category
        existing.status = manifest.status
        existing.required_features = manifest.required_features or []
        existing.required_permissions = manifest.required_permissions or []
        existing.config_schema = manifest.config_schema or {}
        existing.default_config = manifest.default_config or {}
        existing.entrypoint = manifest.entrypoint
        existing.safety_level = manifest.safety_level
        existing.metadata_json = manifest.metadata_json or {}
        existing.source_type = manifest.source_type or "builtin"
        existing.source_ref = manifest.source_ref
        existing.checksum = manifest.checksum
        existing.updated_at = datetime.utcnow()
        result = existing
    else:
        manifest.id = manifest.id or None  # let default _id fire
        db.add(manifest)
        result = manifest

    db.commit()
    db.refresh(result)
    return manifest_to_dict(result)


# ------------------------------------------------------------------ #
# Validation                                                            #
# ------------------------------------------------------------------ #


def validate_plugin_manifest(manifest: dict[str, Any]) -> tuple[bool, list[str]]:
    """Validate a raw manifest dictionary.

    Returns (ok, errors) where *ok* is True when there are zero
    validation errors.
    """
    errors: list[str] = []

    if not manifest.get("name"):
        errors.append("name is required")
    if not manifest.get("slug"):
        errors.append("slug is required")
    if not manifest.get("entrypoint"):
        errors.append("entrypoint is required")
    if not manifest.get("safety_level"):
        errors.append("safety_level is required")

    valid_statuses = {s.value for s in PluginStatus}
    if manifest.get("status") and manifest["status"] not in valid_statuses:
        errors.append(
            f"status must be one of {sorted(valid_statuses)}"
        )

    return (len(errors) == 0, errors)
