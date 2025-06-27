import os
import json
from datetime import datetime
from typing import Dict, List, Optional, Any

class FirestoreService:
    """
    Service class to handle Firestore operations using the REST API
    This allows us to use Firestore without additional dependencies
    """
    
    def __init__(self):
        self.project_id = os.environ.get('FIREBASE_PROJECT_ID')
        self.base_url = f"https://firestore.googleapis.com/v1/projects/{self.project_id}/databases/(default)/documents"
        
    def _make_request(self, method: str, url: str, data: dict = None) -> dict:
        """Make HTTP request to Firestore REST API"""
        import requests
        
        headers = {
            'Content-Type': 'application/json'
        }
        
        try:
            if method == 'GET':
                response = requests.get(url, headers=headers)
            elif method == 'POST':
                response = requests.post(url, headers=headers, json=data)
            elif method == 'PATCH':
                response = requests.patch(url, headers=headers, json=data)
            elif method == 'DELETE':
                response = requests.delete(url, headers=headers)
            
            if response.status_code in [200, 201]:
                return response.json() if response.content else {}
            else:
                print(f"Firestore API error: {response.status_code} - {response.text}")
                return {}
                
        except Exception as e:
            print(f"Firestore request error: {e}")
            return {}
    
    def _convert_to_firestore_value(self, value: Any) -> dict:
        """Convert Python value to Firestore format"""
        if value is None:
            return {"nullValue": None}
        elif isinstance(value, bool):
            return {"booleanValue": value}
        elif isinstance(value, int):
            return {"integerValue": str(value)}
        elif isinstance(value, float):
            return {"doubleValue": value}
        elif isinstance(value, str):
            return {"stringValue": value}
        elif isinstance(value, datetime):
            return {"timestampValue": value.isoformat() + "Z"}
        elif isinstance(value, dict):
            fields = {}
            for k, v in value.items():
                fields[k] = self._convert_to_firestore_value(v)
            return {"mapValue": {"fields": fields}}
        elif isinstance(value, list):
            values = [self._convert_to_firestore_value(v) for v in value]
            return {"arrayValue": {"values": values}}
        else:
            return {"stringValue": str(value)}
    
    def _convert_from_firestore_value(self, firestore_value: dict) -> Any:
        """Convert Firestore value to Python value"""
        if "nullValue" in firestore_value:
            return None
        elif "booleanValue" in firestore_value:
            return firestore_value["booleanValue"]
        elif "integerValue" in firestore_value:
            return int(firestore_value["integerValue"])
        elif "doubleValue" in firestore_value:
            return firestore_value["doubleValue"]
        elif "stringValue" in firestore_value:
            return firestore_value["stringValue"]
        elif "timestampValue" in firestore_value:
            timestamp_str = firestore_value["timestampValue"].replace("Z", "+00:00")
            return datetime.fromisoformat(timestamp_str)
        elif "mapValue" in firestore_value:
            result = {}
            fields = firestore_value["mapValue"].get("fields", {})
            for k, v in fields.items():
                result[k] = self._convert_from_firestore_value(v)
            return result
        elif "arrayValue" in firestore_value:
            values = firestore_value["arrayValue"].get("values", [])
            return [self._convert_from_firestore_value(v) for v in values]
        else:
            return None
    
    def _format_document(self, doc_data: dict) -> dict:
        """Format Firestore document to Python dict"""
        if not doc_data or "fields" not in doc_data:
            return {}
        
        result = {}
        for field_name, field_value in doc_data["fields"].items():
            result[field_name] = self._convert_from_firestore_value(field_value)
        
        # Extract document ID from name
        if "name" in doc_data:
            doc_id = doc_data["name"].split("/")[-1]
            result["id"] = doc_id
            
        return result
    
    def create_document(self, collection: str, document_id: str, data: dict) -> bool:
        """Create a document in Firestore"""
        url = f"{self.base_url}/{collection}"
        
        # Convert data to Firestore format
        firestore_data = {
            "fields": {}
        }
        
        for key, value in data.items():
            firestore_data["fields"][key] = self._convert_to_firestore_value(value)
        
        # Add document ID to URL
        url += f"?documentId={document_id}"
        
        result = self._make_request('POST', url, firestore_data)
        return bool(result)
    
    def get_document(self, collection: str, document_id: str) -> dict:
        """Get a document from Firestore"""
        url = f"{self.base_url}/{collection}/{document_id}"
        result = self._make_request('GET', url)
        return self._format_document(result)
    
    def update_document(self, collection: str, document_id: str, data: dict) -> bool:
        """Update a document in Firestore"""
        url = f"{self.base_url}/{collection}/{document_id}"
        
        # Convert data to Firestore format
        firestore_data = {
            "fields": {}
        }
        
        for key, value in data.items():
            firestore_data["fields"][key] = self._convert_to_firestore_value(value)
        
        result = self._make_request('PATCH', url, firestore_data)
        return bool(result)
    
    def delete_document(self, collection: str, document_id: str) -> bool:
        """Delete a document from Firestore"""
        url = f"{self.base_url}/{collection}/{document_id}"
        result = self._make_request('DELETE', url)
        return True  # DELETE returns 200 even if document doesn't exist
    
    def query_collection(self, collection: str, filters: List[dict] = None, order_by: str = None, limit: int = None) -> List[dict]:
        """Query a collection with optional filters"""
        # For simple queries, we'll list all documents and filter in Python
        # For production, you'd want to use Firestore's structured query API
        url = f"{self.base_url}/{collection}"
        
        if limit:
            url += f"?pageSize={limit}"
        
        result = self._make_request('GET', url)
        documents = []
        
        if "documents" in result:
            for doc in result["documents"]:
                formatted_doc = self._format_document(doc)
                
                # Apply simple filters (for more complex queries, use Firestore structured queries)
                if filters:
                    should_include = True
                    for filter_item in filters:
                        field = filter_item.get("field")
                        operator = filter_item.get("operator", "==")
                        value = filter_item.get("value")
                        
                        doc_value = formatted_doc.get(field)
                        
                        if operator == "==" and doc_value != value:
                            should_include = False
                            break
                        elif operator == "!=" and doc_value == value:
                            should_include = False
                            break
                        elif operator == ">" and not (doc_value and doc_value > value):
                            should_include = False
                            break
                        elif operator == "<" and not (doc_value and doc_value < value):
                            should_include = False
                            break
                    
                    if should_include:
                        documents.append(formatted_doc)
                else:
                    documents.append(formatted_doc)
        
        # Apply ordering if specified
        if order_by and documents:
            reverse = order_by.startswith("-")
            field_name = order_by.lstrip("-")
            documents.sort(key=lambda x: x.get(field_name, ""), reverse=reverse)
        
        return documents
    
    def get_collection_count(self, collection: str) -> int:
        """Get the count of documents in a collection"""
        documents = self.query_collection(collection)
        return len(documents)

# Initialize global Firestore service
firestore_service = FirestoreService()