import hashlib
from .models import KMSKeyRecord
from .kms_adapters import MockKMSAdapter


class KeyManagementService:
    def __init__(self):
        self._keys = []
        self._adapter = MockKMSAdapter()

    def register_key_ref(self, record: KMSKeyRecord):
        self._keys.append(record)
        return record

    def validate_key_ref(self, key_ref: str):
        return len(key_ref.strip()) > 3

    def rotate_key_metadata(self, key_id: str):
        return {"id": key_id, "rotated": True}

    def get_kms_status(self):
        return {"provider": "mock", "records": len(self._keys)}

    def test_kms_connection(self):
        return self._adapter.test()

    @staticmethod
    def hash_ref(key_ref: str):
        return hashlib.sha256(key_ref.encode()).hexdigest()
