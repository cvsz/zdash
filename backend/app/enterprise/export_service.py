from typing import Any

_EXPORTS: list[dict[str, Any]] = []


def list_export_bundles(organization_id):
    return [e for e in _EXPORTS if e["organization_id"] == organization_id]


def create_export_bundle(request):
    if (
        request.get("include_secrets")
        and request.get("confirmation") != "CONFIRM_SECRET_EXPORT"
    ):
        raise ValueError("EXPORT_NOT_ALLOWED")
    item = {"id": f"exp-{len(_EXPORTS) + 1}", **request, "status": "completed"}
    _EXPORTS.append(item)
    return item


def get_export_bundle(organization_id, bundle_id):
    return next(
        (
            e
            for e in _EXPORTS
            if e["organization_id"] == organization_id and e["id"] == bundle_id
        ),
        None,
    )


def import_bundle(file):
    return {"ok": True, "file": str(file)}
