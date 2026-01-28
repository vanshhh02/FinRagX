import os
from app.ingest.hasher import hash_file
from app.ingest.manifest import IngestManifest


class IngestManager:
    def __init__(self):
        self.manifest = IngestManifest()

    def should_ingest(self, path: str):
        filename = os.path.basename(path)
        file_hash = hash_file(path)

        record = self.manifest.get(filename)

        # New document
        if record is None:
            return True, file_hash, 1

        # Changed document
        if record["hash"] != file_hash:
            return True, file_hash, record["version"] + 1

        # Unchanged
        return False, file_hash, record["version"]

    def commit(self, path: str, doc_id: str, file_hash: str):
        filename = os.path.basename(path)
        return self.manifest.update(filename, doc_id, file_hash)
