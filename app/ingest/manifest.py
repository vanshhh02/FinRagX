import json
import os
from datetime import datetime

MANIFEST_PATH = "ingest_manifest.json"


class IngestManifest:
    def __init__(self, path=MANIFEST_PATH):
        self.path = path
        self.data = self._load()

    def _load(self):
        if os.path.exists(self.path):
            with open(self.path, "r") as f:
                return json.load(f)
        return {}

    def save(self):
        with open(self.path, "w") as f:
            json.dump(self.data, f, indent=2)

    def get(self, filename):
        return self.data.get(filename)

    def update(self, filename, doc_id, file_hash):
        record = self.data.get(filename)

        if record is None:
            version = 1
        else:
            version = record["version"] + 1

        self.data[filename] = {
            "doc_id": doc_id,
            "hash": file_hash,
            "version": version,
            "last_ingested": datetime.utcnow().isoformat()
        }

        self.save()
        return version
