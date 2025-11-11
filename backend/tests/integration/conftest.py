"""
Pytest configuration for integration tests using a full in-memory MongoDB replacement.
This version ensures that ALL imports of `db` anywhere in the app
(main.py, routes, services, helpers, etc.) get patched reliably.
"""

import pytest
from unittest.mock import patch
from bson import ObjectId
from copy import deepcopy
import sys
import pkgutil


# ---------------------------------------------------------------------------
# In-memory DB implementation (same behavior as Motor)
# ---------------------------------------------------------------------------
class InMemoryCollection:
    def __init__(self):
        self.data = []

    async def insert_one(self, doc):
        doc = deepcopy(doc)
        if "_id" not in doc:
            doc["_id"] = ObjectId()
        self.data.append(doc)
        return type("Result", (), {"inserted_id": doc["_id"]})

    async def find_one(self, filter_dict):
        for doc in self.data:
            if all(str(doc.get(k)) == str(v) for k, v in filter_dict.items()):
                return deepcopy(doc)
        return None

    async def delete_one(self, filter_dict):
        for i, doc in enumerate(self.data):
            if all(str(doc.get(k)) == str(v) for k, v in filter_dict.items()):
                self.data.pop(i)
                return type("Result", (), {"deleted_count": 1})
        return type("Result", (), {"deleted_count": 0})

    async def update_one(self, filter_dict, update_dict):
        for doc in self.data:
            if all(str(doc.get(k)) == str(v) for k, v in filter_dict.items()):
                if "$set" in update_dict:
                    doc.update(update_dict["$set"])
                else:
                    doc.update(update_dict)
                return type("Result", (), {"modified_count": 1})
        return type("Result", (), {"modified_count": 0})

    async def find(self, filter_dict=None):
        result = []
        for doc in self.data:
            if not filter_dict or all(str(doc.get(k)) == str(v) for k, v in filter_dict.items()):
                result.append(deepcopy(doc))
        return result


class InMemoryDatabase:
    def __init__(self):
        self._collections = {}

    def __getattr__(self, name):
        if name not in self._collections:
            self._collections[name] = InMemoryCollection()
        return self._collections[name]


# ---------------------------------------------------------------------------
# Autouse fixture: replaces ALL db imports everywhere in the project
# ---------------------------------------------------------------------------
@pytest.fixture(scope="session", autouse=True)
def patch_all_db_imports():
    mock_db = InMemoryDatabase()

    patches = []

    # automatically find all modules that imported "db"
    for module in list(sys.modules.values()):
        if not module:
            continue

        if hasattr(module, "db"):
            patches.append(patch.object(module, "db", mock_db))

    # apply all patches
    for p in patches:
        p.start()

    yield mock_db

    # remove patches
    for p in patches:
        p.stop()