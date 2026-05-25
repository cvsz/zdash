class DocsPublishService:
    def publish_docs(self, dry_run: bool = True) -> dict:
        return {"dry_run": dry_run, "status": "queued" if dry_run else "published"}
