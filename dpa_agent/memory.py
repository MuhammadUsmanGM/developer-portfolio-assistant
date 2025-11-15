import datetime
import json
import os

class PersistentMemoryBank:
    def __init__(self, filename="memory_bank.json"):
        self.filename = filename
        self.entries = self._load_entries()

    def _load_entries(self):
        if os.path.isfile(self.filename):
            try:
                with open(self.filename, "r", encoding="utf-8") as f:
                    return json.load(f)
            except:
                return []
        else:
            return []

    def save(self, username, post, meta=None):
        entry = {
            "username": username,
            "post": post,
            "meta": meta or {},
            "timestamp": datetime.datetime.now().isoformat()
        }
        self.entries.append(entry)
        self._persist()
        return entry

    def _persist(self):
        try:
            with open(self.filename, "w", encoding="utf-8") as f:
                json.dump(self.entries, f, indent=2)
        except Exception as e:
            print(f"Error saving memory: {str(e)}")

    def get_history(self, username=None):
        if username:
            return [e for e in self.entries if e["username"] == username]
        return self.entries
