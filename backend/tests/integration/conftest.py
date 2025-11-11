"""
Pytest configuration and fixtures for integration tests.
Sets up a mock in-memory database using pure Python (no external dependencies).
"""
import pytest
from unittest.mock import patch, MagicMock
from bson import ObjectId
from typing import Dict, List, Any, Optional
from copy import deepcopy


@pytest.fixture(scope="function", autouse=True)
def mock_database():
    """Replace the real database with an in-memory mock for all integration tests"""
    
    class InMemoryDatabase:
        """In-memory database that mimics MongoDB/Motor behavior"""
        def __init__(self):
            self._collections: Dict[str, List[Dict]] = {}
        
        def __getattr__(self, name: str):
            """Dynamically create collections as attributes"""
            if name not in self._collections:
                self._collections[name] = []
            return InMemoryCollection(self._collections[name])
        
        def __getitem__(self, name: str):
            """Allow dictionary-style access"""
            return self.__getattr__(name)
    
    class InMemoryCollection:
        """In-memory collection that mimics Motor collection behavior"""
        def __init__(self, storage: List[Dict]):
            self._storage = storage
        
        async def find_one(self, filter_dict: Dict) -> Optional[Dict]:
            """Find a single document matching the filter"""
            filter_dict = self._convert_filter(filter_dict)
            for doc in self._storage:
                if self._matches(doc, filter_dict):
                    return deepcopy(doc)
            return None
        
        async def insert_one(self, document: Dict) -> MagicMock:
            """Insert a single document"""
            # Deep copy to avoid reference issues
            doc_copy = deepcopy(document)
            # Ensure _id exists
            if "_id" not in doc_copy:
                doc_copy["_id"] = ObjectId()
            self._storage.append(doc_copy)
            return MagicMock(inserted_id=doc_copy["_id"])
        
        async def update_one(self, filter_dict: Dict, update_dict: Dict) -> MagicMock:
            """Update a single document"""
            # Convert ObjectId strings to ObjectId objects in filter
            from bson import ObjectId
            converted_filter = {}
            for key, value in filter_dict.items():
                if key == "_id":
                    converted_filter[key] = ObjectId(value) if isinstance(value, str) else value
                else:
                    converted_filter[key] = value
            
            # Handle $set operator
            if "$set" in update_dict:
                set_dict = update_dict["$set"]
                # Update document
                doc = self._find_doc(converted_filter)
                if doc:
                    doc.update(set_dict)
                    return MagicMock(modified_count=1)
                return MagicMock(modified_count=0)
            else:
                doc = self._find_doc(converted_filter)
                if doc:
                    doc.update(update_dict)
                    return MagicMock(modified_count=1)
                return MagicMock(modified_count=0)
        
        async def delete_one(self, filter_dict: Dict) -> MagicMock:
            """Delete a single document"""
            filter_dict = self._convert_filter(filter_dict)
            
            for i, doc in enumerate(self._storage):
                if self._matches(doc, filter_dict):
                    self._storage.pop(i)
                    return MagicMock(deleted_count=1)
            return MagicMock(deleted_count=0)
        
        async def find(self, filter_dict: Dict = None) -> 'InMemoryCursor':
            """Find multiple documents"""
            filter_dict = self._convert_filter(filter_dict) if filter_dict else {}
            matching_docs = [
                deepcopy(doc) for doc in self._storage
                if self._matches(doc, filter_dict)
            ]
            return InMemoryCursor(matching_docs)
        
        async def insert_many(self, documents: List[Dict]) -> MagicMock:
            """Insert multiple documents"""
            inserted_ids = []
            for doc in documents:
                doc_copy = deepcopy(doc)
                if "_id" not in doc_copy:
                    doc_copy["_id"] = ObjectId()
                inserted_ids.append(doc_copy["_id"])
                self._storage.append(doc_copy)
            return MagicMock(inserted_ids=inserted_ids)
        
        def _find_doc(self, filter_dict: Dict) -> Optional[Dict]:
            """Find a document in storage"""
            for doc in self._storage:
                if self._matches(doc, filter_dict):
                    return doc
            return None
        
        def _convert_filter(self, filter_dict: Dict) -> Dict:
            """Convert filter dictionary, handling ObjectId strings"""
            converted = {}
            for key, value in filter_dict.items():
                if key == "_id" and isinstance(value, str):
                    try:
                        converted[key] = ObjectId(value)
                    except:
                        converted[key] = value
                elif key == "_id" and isinstance(value, ObjectId):
                    converted[key] = value
                else:
                    converted[key] = value
            return converted
        
        def _matches(self, doc: Dict, filter_dict: Dict) -> bool:
            """Check if a document matches the filter"""
            for key, value in filter_dict.items():
                if key not in doc:
                    return False
                # Handle ObjectId comparison
                if isinstance(value, ObjectId) or isinstance(doc[key], ObjectId):
                    if str(doc[key]) != str(value):
                        return False
                elif doc[key] != value:
                    return False
            return True
    
    class InMemoryCursor:
        """Cursor-like object for iterating over query results"""
        def __init__(self, data: List[Dict]):
            self._data = data
            self._index = 0
        
        def sort(self, *args, **kwargs):
            """Sort the cursor (returns self for chaining)"""
            if args:
                field = args[0]
                reverse = len(args) > 1 and args[1] == -1
                self._data.sort(key=lambda x: x.get(field, ""), reverse=reverse)
            return self
        
        def skip(self, n: int):
            """Skip n documents (returns self for chaining)"""
            self._data = self._data[n:]
            return self
        
        def limit(self, n: int):
            """Limit to n documents (returns self for chaining)"""
            self._data = self._data[:n]
            return self
        
        async def to_list(self, length: Optional[int] = None) -> List[Dict]:
            """Convert cursor to list"""
            if length is None:
                return self._data
            return self._data[:length]
    
    # Create the mock database
    mock_db = InMemoryDatabase()
    
    # Patch database in all relevant modules
    with patch('database.db', mock_db):
        with patch('routes.orders.db', mock_db):
            with patch('main.db', mock_db):
                yield mock_db
