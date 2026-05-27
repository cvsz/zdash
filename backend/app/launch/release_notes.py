class ReleaseNotesService:
    def generate_release_notes(self, from_version: str, to_version: str) -> dict:
        return {
            "from": from_version,
            "to": to_version,
            "notes": ["Phase 14 launch shell updates"],
        }
