from __future__ import annotations

from sqlalchemy import create_engine
from sqlalchemy.orm import Session

from app.db.base import Base
from app.marketplace.builtins import BUILTINS
from app.marketplace.models import PluginManifest, PluginStatus, manifest_to_dict
from app.marketplace.plugin_registry import (
    get_plugin,
    list_plugins,
    register_plugin_manifest,
    seed_builtins,
    validate_plugin_manifest,
)


def _memory_session() -> Session:
    engine = create_engine("sqlite://", future=True)
    Base.metadata.create_all(bind=engine)
    return Session(engine)


def test_seed_builtins_inserts_all():
    db = _memory_session()
    seeded = seed_builtins(db)
    assert len(seeded) == len(BUILTINS)
    slugs = {s["slug"] for s in seeded}
    for b in BUILTINS:
        assert b.slug in slugs


def test_seed_builtins_idempotent():
    db = _memory_session()
    seed_builtins(db)
    seeded2 = seed_builtins(db)
    assert seeded2 == []


def test_list_plugins_returns_all():
    db = _memory_session()
    seed_builtins(db)
    all_plugins = list_plugins(db)
    assert len(all_plugins) == len(BUILTINS)


def test_list_plugins_search_filter():
    db = _memory_session()
    seed_builtins(db)
    results = list_plugins(db, search="risk")
    assert all(
        "risk" in p.name.lower()
        or "risk" in p.description.lower()
        or "risk" in p.slug.lower()
        for p in results
    )


def test_list_plugins_category_filter():
    db = _memory_session()
    seed_builtins(db)
    risk_plugins = list_plugins(db, category="risk")
    assert all(p.category == "risk" for p in risk_plugins)


def test_list_plugins_status_filter():
    db = _memory_session()
    seed_builtins(db)
    approved = list_plugins(db, status="approved")
    assert all(p.status == "approved" for p in approved)


def test_get_plugin_by_id():
    db = _memory_session()
    seed_builtins(db)
    first = BUILTINS[0]
    found = get_plugin(db, first.id)
    assert found is not None
    assert found.id == first.id
    assert found.name == first.name


def test_get_plugin_not_found():
    db = _memory_session()
    seed_builtins(db)
    found = get_plugin(db, "nonexistent-id")
    assert found is None


def test_register_new_manifest():
    db = _memory_session()
    manifest = PluginManifest(
        name="Test New Plugin",
        slug="test-new-plugin",
        version="1.0.0",
        description="A new test plugin",
        author="tester",
        category="general",
        status=PluginStatus.draft.value,
        entrypoint="builtin://test",
        safety_level="sandbox",
    )
    result = register_plugin_manifest(db, manifest, actor="tester")
    assert result["name"] == "Test New Plugin"
    assert result["slug"] == "test-new-plugin"


def test_register_manifest_upsert_by_slug():
    db = _memory_session()
    seed_builtins(db)
    first_builtin = BUILTINS[0]

    manifest = PluginManifest(
        name="Updated Name",
        slug=first_builtin.slug,
        version="2.0.0",
        description="Updated description",
        author="updater",
        category="general",
        status=PluginStatus.approved.value,
        entrypoint="builtin://updated",
        safety_level="restricted",
    )
    result = register_plugin_manifest(db, manifest, actor="updater")
    assert result["name"] == "Updated Name"
    assert result["version"] == "2.0.0"


def test_validate_plugin_manifest_valid():
    ok, errors = validate_plugin_manifest(
        {
            "name": "Valid Plugin",
            "slug": "valid-plugin",
            "entrypoint": "builtin://valid",
            "safety_level": "sandbox",
            "status": "approved",
        }
    )
    assert ok is True
    assert errors == []


def test_validate_plugin_manifest_missing_fields():
    ok, errors = validate_plugin_manifest({})
    assert ok is False
    assert len(errors) >= 3


def test_validate_plugin_manifest_invalid_status():
    ok, errors = validate_plugin_manifest(
        {
            "name": "Bad",
            "slug": "bad",
            "entrypoint": "builtin://bad",
            "safety_level": "sandbox",
            "status": "nonexistent",
        }
    )
    assert ok is False
    assert any("status" in e for e in errors)


def test_manifest_to_dict_includes_new_fields():
    db = _memory_session()
    seed_builtins(db)
    first = list_plugins(db)[0]
    d = manifest_to_dict(first)
    assert "source_type" in d
    assert d["source_type"] == "builtin"
    assert "source_ref" in d
    assert "checksum" in d
