import hashlib

_LICENSES: dict[str, dict[str, str]] = {}


def get_license_status(organization_id):
    return _LICENSES.get(organization_id, {"status": "none"})


def apply_license(organization_id, license_key):
    _LICENSES[organization_id] = {
        "status": "active",
        "license_key_hash": hashlib.sha256(license_key.encode()).hexdigest(),
    }
    return _LICENSES[organization_id]


def validate_license(organization_id):
    return get_license_status(organization_id)


def revoke_license(organization_id):
    _LICENSES[organization_id] = {"status": "revoked"}
    return _LICENSES[organization_id]
