from datetime import datetime
from typing import Dict, List, Optional, Any
from firestore_service import firestore_service

class FirestoreModel:
    """Base class for Firestore models"""
    
    collection_name = None
    
    def __init__(self, **kwargs):
        self.id = kwargs.get('id')
        for key, value in kwargs.items():
            setattr(self, key, value)
    
    @classmethod
    def create(cls, data: dict) -> 'FirestoreModel':
        """Create a new document"""
        document_id = data.get('id') or cls._generate_id()
        
        # Add timestamps
        now = datetime.now()
        data['created_at'] = now
        data['updated_at'] = now
        
        success = firestore_service.create_document(cls.collection_name, document_id, data)
        if success:
            return cls(id=document_id, **data)
        return None
    
    @classmethod
    def get(cls, document_id: str) -> Optional['FirestoreModel']:
        """Get a document by ID"""
        data = firestore_service.get_document(cls.collection_name, document_id)
        if data:
            return cls(**data)
        return None
    
    @classmethod
    def query(cls, filters: List[dict] = None, order_by: str = None, limit: int = None) -> List['FirestoreModel']:
        """Query collection with filters"""
        documents = firestore_service.query_collection(cls.collection_name, filters, order_by, limit)
        return [cls(**doc) for doc in documents]
    
    @classmethod
    def get_all(cls) -> List['FirestoreModel']:
        """Get all documents in collection"""
        return cls.query()
    
    def save(self) -> bool:
        """Save the current model to Firestore"""
        if not self.id:
            self.id = self._generate_id()
            return self._create()
        else:
            return self._update()
    
    def delete(self) -> bool:
        """Delete the document"""
        if self.id:
            return firestore_service.delete_document(self.collection_name, self.id)
        return False
    
    def _create(self) -> bool:
        """Internal create method"""
        data = self.to_dict()
        data.pop('id', None)  # Remove ID from data
        
        now = datetime.now()
        data['created_at'] = now
        data['updated_at'] = now
        
        return firestore_service.create_document(self.collection_name, self.id, data)
    
    def _update(self) -> bool:
        """Internal update method"""
        data = self.to_dict()
        data.pop('id', None)  # Remove ID from data
        data['updated_at'] = datetime.now()
        
        return firestore_service.update_document(self.collection_name, self.id, data)
    
    def to_dict(self) -> dict:
        """Convert model to dictionary"""
        result = {}
        for key, value in self.__dict__.items():
            if not key.startswith('_'):
                result[key] = value
        return result
    
    @staticmethod
    def _generate_id() -> str:
        """Generate a unique ID"""
        import uuid
        return str(uuid.uuid4())

class User(FirestoreModel):
    """User model for Firestore"""
    
    collection_name = "users"
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.email = kwargs.get('email')
        self.first_name = kwargs.get('first_name')
        self.last_name = kwargs.get('last_name')
        self.profile_image_url = kwargs.get('profile_image_url')
        self.phone_number = kwargs.get('phone_number')
        self.is_verified = kwargs.get('is_verified', False)
        self.trust_score = kwargs.get('trust_score', 5.0)
        self.current_latitude = kwargs.get('current_latitude')
        self.current_longitude = kwargs.get('current_longitude')
        self.location_updated_at = kwargs.get('location_updated_at')
        self.created_at = kwargs.get('created_at')
        self.updated_at = kwargs.get('updated_at')
    
    @classmethod
    def get_by_email(cls, email: str) -> Optional['User']:
        """Get user by email"""
        users = cls.query([{"field": "email", "operator": "==", "value": email}])
        return users[0] if users else None
    
    def get_exchange_requests(self) -> List['ExchangeRequest']:
        """Get all exchange requests for this user"""
        return ExchangeRequest.query([{"field": "user_id", "operator": "==", "value": self.id}])
    
    def get_matches_as_requester(self) -> List['ExchangeMatch']:
        """Get matches where user is requester"""
        return ExchangeMatch.query([{"field": "requester_id", "operator": "==", "value": self.id}])
    
    def get_matches_as_provider(self) -> List['ExchangeMatch']:
        """Get matches where user is provider"""
        return ExchangeMatch.query([{"field": "provider_id", "operator": "==", "value": self.id}])
    
    def update_location(self, latitude: float, longitude: float) -> bool:
        """Update user's current location"""
        self.current_latitude = latitude
        self.current_longitude = longitude
        self.location_updated_at = datetime.now()
        return self.save()

class ExchangeRequest(FirestoreModel):
    """Exchange Request model for Firestore"""
    
    collection_name = "exchange_requests"
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.user_id = kwargs.get('user_id')
        self.have_amount = kwargs.get('have_amount')
        self.have_denomination = kwargs.get('have_denomination')
        self.want_amount = kwargs.get('want_amount')
        self.want_denomination = kwargs.get('want_denomination')
        self.exchange_latitude = kwargs.get('exchange_latitude')
        self.exchange_longitude = kwargs.get('exchange_longitude')
        self.exchange_location_name = kwargs.get('exchange_location_name')
        self.status = kwargs.get('status', 'active')
        self.expires_at = kwargs.get('expires_at')
        self.notes = kwargs.get('notes')
        self.preferred_safe_zones = kwargs.get('preferred_safe_zones')
        self.created_at = kwargs.get('created_at')
        self.updated_at = kwargs.get('updated_at')
    
    @classmethod
    def get_active_requests(cls) -> List['ExchangeRequest']:
        """Get all active exchange requests"""
        return cls.query([{"field": "status", "operator": "==", "value": "active"}])
    
    @classmethod
    def get_nearby_requests(cls, latitude: float, longitude: float, radius_km: float = 10) -> List['ExchangeRequest']:
        """Get requests near a location (simplified - in production use geoqueries)"""
        # For now, get all active requests and filter by distance
        active_requests = cls.get_active_requests()
        nearby = []
        
        for request in active_requests:
            if request.exchange_latitude and request.exchange_longitude:
                distance = cls._calculate_distance(
                    latitude, longitude,
                    request.exchange_latitude, request.exchange_longitude
                )
                if distance <= radius_km:
                    nearby.append(request)
        
        return nearby
    
    @staticmethod
    def _calculate_distance(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
        """Calculate distance between two points in km"""
        import math
        
        R = 6371  # Earth's radius in km
        
        dlat = math.radians(lat2 - lat1)
        dlon = math.radians(lon2 - lon1)
        
        a = (math.sin(dlat / 2) * math.sin(dlat / 2) +
             math.cos(math.radians(lat1)) * math.cos(math.radians(lat2)) *
             math.sin(dlon / 2) * math.sin(dlon / 2))
        
        c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
        distance = R * c
        
        return distance
    
    def get_user(self) -> Optional[User]:
        """Get the user who created this request"""
        return User.get(self.user_id)
    
    def get_matches(self) -> List['ExchangeMatch']:
        """Get all matches for this request"""
        return ExchangeMatch.query([{"field": "request_id", "operator": "==", "value": self.id}])

class ExchangeMatch(FirestoreModel):
    """Exchange Match model for Firestore"""
    
    collection_name = "exchange_matches"
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.request_id = kwargs.get('request_id')
        self.requester_id = kwargs.get('requester_id')
        self.provider_id = kwargs.get('provider_id')
        self.status = kwargs.get('status', 'pending')
        self.distance_km = kwargs.get('distance_km')
        self.matched_at = kwargs.get('matched_at')
        self.confirmed_at = kwargs.get('confirmed_at')
        self.completed_at = kwargs.get('completed_at')
        self.chat_active = kwargs.get('chat_active', False)
        self.requester_rating = kwargs.get('requester_rating')
        self.provider_rating = kwargs.get('provider_rating')
        self.requester_feedback = kwargs.get('requester_feedback')
        self.provider_feedback = kwargs.get('provider_feedback')
        self.created_at = kwargs.get('created_at')
        self.updated_at = kwargs.get('updated_at')
    
    def get_request(self) -> Optional[ExchangeRequest]:
        """Get the associated exchange request"""
        return ExchangeRequest.get(self.request_id)
    
    def get_requester(self) -> Optional[User]:
        """Get the requester user"""
        return User.get(self.requester_id)
    
    def get_provider(self) -> Optional[User]:
        """Get the provider user"""
        return User.get(self.provider_id)
    
    def confirm(self) -> bool:
        """Confirm the match"""
        self.status = 'confirmed'
        self.confirmed_at = datetime.now()
        return self.save()
    
    def complete(self) -> bool:
        """Mark the match as completed"""
        self.status = 'completed'
        self.completed_at = datetime.now()
        return self.save()

class Notification(FirestoreModel):
    """Notification model for Firestore"""
    
    collection_name = "notifications"
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.user_id = kwargs.get('user_id')
        self.title = kwargs.get('title')
        self.message = kwargs.get('message')
        self.type = kwargs.get('type')
        self.related_request_id = kwargs.get('related_request_id')
        self.related_match_id = kwargs.get('related_match_id')
        self.is_read = kwargs.get('is_read', False)
        self.created_at = kwargs.get('created_at')
    
    @classmethod
    def get_user_notifications(cls, user_id: str, limit: int = 20) -> List['Notification']:
        """Get notifications for a user"""
        return cls.query(
            filters=[{"field": "user_id", "operator": "==", "value": user_id}],
            order_by="-created_at",
            limit=limit
        )
    
    @classmethod
    def get_unread_count(cls, user_id: str) -> int:
        """Get count of unread notifications for a user"""
        notifications = cls.query([
            {"field": "user_id", "operator": "==", "value": user_id},
            {"field": "is_read", "operator": "==", "value": False}
        ])
        return len(notifications)
    
    def mark_read(self) -> bool:
        """Mark notification as read"""
        self.is_read = True
        return self.save()

class ChatMessage(FirestoreModel):
    """Chat Message model for Firestore"""
    
    collection_name = "chat_messages"
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.match_id = kwargs.get('match_id')
        self.sender_id = kwargs.get('sender_id')
        self.message = kwargs.get('message')
        self.message_type = kwargs.get('message_type', 'text')
        self.created_at = kwargs.get('created_at')
    
    @classmethod
    def get_match_messages(cls, match_id: str) -> List['ChatMessage']:
        """Get all messages for a match"""
        return cls.query(
            filters=[{"field": "match_id", "operator": "==", "value": match_id}],
            order_by="created_at"
        )
    
    def get_sender(self) -> Optional[User]:
        """Get the sender user"""
        return User.get(self.sender_id)
    
    def get_match(self) -> Optional[ExchangeMatch]:
        """Get the associated match"""
        return ExchangeMatch.get(self.match_id)