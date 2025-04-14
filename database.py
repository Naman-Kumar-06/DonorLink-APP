import os
from datetime import datetime
import json
import uuid  # For generating unique IDs
import streamlit as st

# Firebase configuration - keep this for reference
firebase_config = {
    "apiKey": "AIzaSyBQTVqNM-vlWcHXLvYqM8kGkPCX_VVROcQ",
    "authDomain": "bloodbank9090.firebaseapp.com",
    "projectId": "bloodbank9090",
    "storageBucket": "bloodbank9090.appspot.com",
    "messagingSenderId": "268077674400",
    "appId": "1:268077674400:web:54421a2a982b140b6b3ec5",
    "measurementId": "G-XY4QZ9Q785",
    "databaseURL": ""  # Required for Pyrebase initialization but not used
}

# Initialize mock database storage in session state for persistence within the session
def initialize_firebase():
    """Initialize mock Firebase services for demonstration purposes."""
    # Initialize session state for mock database if not exists
    if 'mock_db' not in st.session_state:
        st.session_state.mock_db = {
            'users': {},
            'blood_requests': {},
            'inventory': {
                'blood_inventory': {
                    "A+": 10,
                    "A-": 5,
                    "B+": 8,
                    "B-": 4,
                    "AB+": 3,
                    "AB-": 2,
                    "O+": 15,
                    "O-": 7,
                    "last_updated": datetime.now().isoformat()
                }
            }
        }
        
        # Create sample admin user
        admin_id = str(uuid.uuid4())
        st.session_state.mock_db['users'][admin_id] = {
            'id': admin_id,
            'name': 'Admin User',
            'email': 'admin@bloodbank.com',
            'role': 'admin',
            'phone': '555-123-4567',
            'address': '123 Hospital St',
            'city': 'Medical City',
            'created_at': datetime.now().isoformat()
        }
    
    print("Mock Firebase initialized successfully")
    return True

class MockDocument:
    """Mock Firestore document for simulating Firestore operations."""
    def __init__(self, doc_id, data=None, collection_name=None):
        self.id = doc_id
        self._data = data or {}
        self.exists = data is not None
        self.collection_name = collection_name
        self.parent_doc = None  # Reference to parent document for subcollections

    def get(self):
        return self
        
    def to_dict(self):
        return self._data
        
    def set(self, data, merge=False):
        if merge and self._data:
            # Update existing data
            self._data.update(data)
        else:
            # Replace with new data
            self._data = data
        
        # Update exists status
        self.exists = True
        
        # Persist to session state
        if self.collection_name:
            # Initialize collections if they don't exist
            if 'users' not in st.session_state.mock_db:
                st.session_state.mock_db['users'] = {}
            if 'blood_requests' not in st.session_state.mock_db:
                st.session_state.mock_db['blood_requests'] = {}
            if 'inventory' not in st.session_state.mock_db:
                st.session_state.mock_db['inventory'] = {}
                
            # Handle top-level collections
            if self.collection_name == 'users':
                st.session_state.mock_db['users'][self.id] = self._data
            elif self.collection_name == 'blood_requests':
                st.session_state.mock_db['blood_requests'][self.id] = self._data
            elif self.collection_name == 'inventory':
                st.session_state.mock_db['inventory'][self.id] = self._data
            # Handle subcollections - will be implemented via parent document reference
            
        return True
        
    def update(self, data):
        # Update data
        if not self._data:
            self._data = {}
        self._data.update(data)
        
        # Persist to session state
        if self.collection_name:
            if self.collection_name == 'users':
                if self.id in st.session_state.mock_db['users']:
                    st.session_state.mock_db['users'][self.id].update(data)
                else:
                    st.session_state.mock_db['users'][self.id] = self._data
            elif self.collection_name == 'blood_requests':
                if self.id in st.session_state.mock_db['blood_requests']:
                    st.session_state.mock_db['blood_requests'][self.id].update(data)
                else:
                    st.session_state.mock_db['blood_requests'][self.id] = self._data
            elif self.collection_name == 'inventory':
                if self.id in st.session_state.mock_db['inventory']:
                    st.session_state.mock_db['inventory'][self.id].update(data)
                else:
                    st.session_state.mock_db['inventory'][self.id] = self._data
        
        return True
        
    def collection(self, collection_name):
        return MockCollection(collection_name, parent_doc=self)

class MockDocumentSnapshot:
    """Mock document snapshot returned from queries."""
    def __init__(self, doc_id, data):
        self.id = doc_id
        self._data = data
        self.exists = True
        
    def to_dict(self):
        return self._data

class MockQuery:
    """Mock query for simulating Firestore queries."""
    def __init__(self, collection_name, filters=None):
        self.collection_name = collection_name
        self.filters = filters or []
        self.order_params = []
        
    def where(self, field, op, value):
        self.filters.append((field, op, value))
        return self
        
    def order_by(self, field, direction=None):
        self.order_params.append((field, direction))
        return self
        
    def get(self):
        collection_data = self._get_collection_data()
        
        # Apply filters
        filtered_data = collection_data
        for field, op, value in self.filters:
            if op == '==':
                filtered_data = {k: v for k, v in filtered_data.items() 
                                if field in v and v[field] == value}
        
        # Convert to document snapshots
        return [MockDocumentSnapshot(doc_id, data) for doc_id, data in filtered_data.items()]
    
    def _get_collection_data(self):
        # Access data from session state based on collection path
        if self.collection_name == 'users':
            return st.session_state.mock_db.get('users', {})
        elif self.collection_name == 'blood_requests':
            return st.session_state.mock_db.get('blood_requests', {})
        elif self.collection_name == 'inventory':
            return st.session_state.mock_db.get('inventory', {})
        return {}

class MockCollection:
    """Mock collection for simulating Firestore collections."""
    def __init__(self, name, parent_doc=None):
        self.name = name
        self.parent_doc = parent_doc
        
    def document(self, doc_id=None):
        if not doc_id:
            doc_id = str(uuid.uuid4())
        
        # Initialize the collection in mock_db if it doesn't exist
        if self.name == 'users' and 'users' not in st.session_state.mock_db:
            st.session_state.mock_db['users'] = {}
        elif self.name == 'blood_requests' and 'blood_requests' not in st.session_state.mock_db:
            st.session_state.mock_db['blood_requests'] = {}
        elif self.name == 'inventory' and 'inventory' not in st.session_state.mock_db:
            st.session_state.mock_db['inventory'] = {}
        
        # Get document data if it exists
        collection_data = self._get_collection_data()
        doc_data = collection_data.get(doc_id)
        
        # For inventory/blood_inventory, create it if it doesn't exist
        if self.name == 'inventory' and doc_id == 'blood_inventory' and not doc_data:
            doc_data = {
                "A+": 10,
                "A-": 5,
                "B+": 8,
                "B-": 4,
                "AB+": 3,
                "AB-": 2,
                "O+": 15,
                "O-": 7,
                "last_updated": datetime.now().isoformat()
            }
            st.session_state.mock_db['inventory']['blood_inventory'] = doc_data
        
        # Determine the collection name to pass to MockDocument
        collection_name = None
        if self.parent_doc:
            # For subcollections like notifications
            if self.parent_doc.collection_name == 'users' and self.name == 'notifications':
                collection_name = 'notifications'
        else:
            # For top-level collections
            collection_name = self.name
        
        return MockDocument(doc_id, doc_data, collection_name)
    
    def where(self, field, op, value):
        return MockQuery(self.name, [(field, op, value)])
    
    def order_by(self, field, direction=None):
        query = MockQuery(self.name)
        query.order_by(field, direction)
        return query
    
    def get(self):
        collection_data = self._get_collection_data()
        return [MockDocumentSnapshot(doc_id, data) for doc_id, data in collection_data.items()]
    
    def _get_collection_data(self):
        # Access data from session state based on collection path
        if self.parent_doc:
            # Handle subcollections (e.g., notifications)
            if self.name == 'notifications':
                # Ensure parent document exists
                if self.parent_doc.id in st.session_state.mock_db.get('users', {}):
                    # Create notifications subcollection if it doesn't exist
                    if 'notifications' not in st.session_state.mock_db['users'][self.parent_doc.id]:
                        st.session_state.mock_db['users'][self.parent_doc.id]['notifications'] = {}
                    return st.session_state.mock_db['users'][self.parent_doc.id]['notifications']
                return {}
        elif self.name == 'users':
            return st.session_state.mock_db.get('users', {})
        elif self.name == 'blood_requests':
            return st.session_state.mock_db.get('blood_requests', {})
        elif self.name == 'inventory':
            return st.session_state.mock_db.get('inventory', {})
        return {}

class MockFirestore:
    """Mock Firestore client for simulating Firestore database operations."""
    def collection(self, collection_name):
        return MockCollection(collection_name)

class MockAuthUser:
    """Mock Firebase Auth user object."""
    def __init__(self, email, user_id):
        self.email = email
        self.uid = user_id
        self.localId = user_id  # Matches Firebase format

class MockAuth:
    """Mock Firebase Auth for simulating authentication operations."""
    def sign_in_with_email_and_password(self, email, password):
        # Find user with matching email
        for user_id, user_data in st.session_state.mock_db['users'].items():
            if user_data.get('email') == email:
                # In a real app, we'd verify the password here, but for demo we'll accept any password
                return {'localId': user_id, 'email': email}
        
        # Create default users if they don't exist - for demo purposes
        if email == "admin@bloodbank.com":
            admin_id = str(uuid.uuid4())
            st.session_state.mock_db['users'][admin_id] = {
                'id': admin_id,
                'name': 'Admin User',
                'email': 'admin@bloodbank.com',
                'role': 'admin',
                'phone': '555-123-4567',
                'address': '123 Hospital St',
                'city': 'Medical City',
                'created_at': datetime.now().isoformat()
            }
            return {'localId': admin_id, 'email': email}
        elif email == "donor@bloodbank.com":
            donor_id = str(uuid.uuid4())
            st.session_state.mock_db['users'][donor_id] = {
                'id': donor_id,
                'name': 'John Donor',
                'email': 'donor@bloodbank.com',
                'role': 'donor',
                'phone': '555-222-3333',
                'blood_group': 'O+',
                'available': True,
                'address': '456 Donor Ave',
                'city': 'Blood City',
                'donation_history': [],
                'created_at': datetime.now().isoformat()
            }
            return {'localId': donor_id, 'email': email}
        elif email == "receiver@bloodbank.com":
            receiver_id = str(uuid.uuid4())
            st.session_state.mock_db['users'][receiver_id] = {
                'id': receiver_id,
                'name': 'Hospital Receiver',
                'email': 'receiver@bloodbank.com',
                'role': 'receiver',
                'phone': '555-444-5555',
                'organization': 'City Hospital',
                'address': '789 Hospital Blvd',
                'city': 'Medical City',
                'request_history': [],
                'created_at': datetime.now().isoformat()
            }
            return {'localId': receiver_id, 'email': email}
        
        # If no match and not a default user
        raise Exception("EMAIL_NOT_FOUND")
    
    def create_user_with_email_and_password(self, email, password):
        # Check if email already exists
        for user_data in st.session_state.mock_db['users'].values():
            if user_data.get('email') == email:
                raise Exception("EMAIL_EXISTS")
        
        # Create new user
        user_id = str(uuid.uuid4())
        # Add the user to session state
        if 'users' not in st.session_state.mock_db:
            st.session_state.mock_db['users'] = {}
            
        return {'localId': user_id, 'email': email}

def get_firestore_db():
    """Get the mock Firestore database instance."""
    # Always initialize Firebase first to ensure session state is set up
    initialize_firebase()
    return MockFirestore()

def get_auth():
    """Get the mock Firebase Authentication instance."""
    # Always initialize Firebase first to ensure session state is set up
    initialize_firebase()
    return MockAuth()

def get_admin_auth():
    """Get the Firebase Admin Auth instance (for admin operations)."""
    # Not fully implemented in mock version
    return None

def get_server_timestamp():
    """Get a server timestamp."""
    return datetime.now().isoformat()

# User Management Functions
def get_user_by_id(user_id):
    """Get a user's data by their ID."""
    try:
        db = get_firestore_db()
        user_doc = db.collection('users').document(user_id).get()
        if user_doc.exists:
            return user_doc.to_dict()
        return None
    except Exception as e:
        print(f"Error in get_user_by_id: {str(e)}")
        return None

def update_user_profile(user_id, data):
    """Update a user's profile data."""
    try:
        db = get_firestore_db()
        db.collection('users').document(user_id).update(data)
        return True
    except Exception as e:
        print(f"Error in update_user_profile: {str(e)}")
        return False

# Blood Inventory Functions
def get_blood_inventory():
    """Get the current blood inventory."""
    try:
        db = get_firestore_db()
        inventory_ref = db.collection('inventory').document('blood_inventory').get()
        if inventory_ref.exists:
            inventory_data = inventory_ref.to_dict()
            # Remove non-blood group fields if any
            for key in list(inventory_data.keys()):
                if key not in ["A+", "A-", "B+", "B-", "AB+", "AB-", "O+", "O-"]:
                    inventory_data.pop(key)
            return inventory_data
        return {}
    except Exception as e:
        print(f"Error in get_blood_inventory: {str(e)}")
        return {}

def update_blood_inventory(inventory_data):
    """Update the blood inventory."""
    try:
        db = get_firestore_db()
        inventory_data['last_updated'] = get_server_timestamp()
        db.collection('inventory').document('blood_inventory').update(inventory_data)
        return True
    except Exception as e:
        print(f"Error in update_blood_inventory: {str(e)}")
        return False

# Blood Request Functions
def create_blood_request(request_data):
    """Create a new blood request."""
    try:
        db = get_firestore_db()
        request_ref = db.collection('blood_requests').document()
        request_data['request_id'] = request_ref.id
        request_data['created_at'] = get_server_timestamp()
        request_data['status'] = 'pending'
        request_ref.set(request_data)
        
        # Update user's request history
        user_ref = db.collection('users').document(request_data['user_id'])
        user_data = user_ref.get().to_dict()
        
        if user_data:
            request_history = user_data.get('request_history', [])
            request_history.append({
                'request_id': request_ref.id,
                'blood_group': request_data['blood_group'],
                'units': request_data['units'],
                'created_at': datetime.now().isoformat(),
                'status': 'pending'
            })
            user_ref.update({'request_history': request_history})
        
        return request_ref.id
    except Exception as e:
        print(f"Error in create_blood_request: {str(e)}")
        raise

def get_blood_requests(status=None):
    """Get blood requests with optional status filter."""
    try:
        db = get_firestore_db()
        if status:
            requests_ref = db.collection('blood_requests').where('status', '==', status)
        else:
            requests_ref = db.collection('blood_requests')
        
        # Get all requests
        requests = requests_ref.get()
        return [doc.to_dict() for doc in requests]
    except Exception as e:
        print(f"Error in get_blood_requests: {str(e)}")
        return []

def get_blood_request(request_id):
    """Get a specific blood request by ID."""
    try:
        db = get_firestore_db()
        request_doc = db.collection('blood_requests').document(request_id).get()
        if request_doc.exists:
            return request_doc.to_dict()
        return None
    except Exception as e:
        print(f"Error in get_blood_request: {str(e)}")
        return None

def update_blood_request(request_id, data):
    """Update a blood request."""
    try:
        db = get_firestore_db()
        request_ref = db.collection('blood_requests').document(request_id)
        request_doc = request_ref.get()
        
        if not request_doc.exists:
            return False
        
        request_ref.update(data)
        
        # If status is changing, update request in user's history
        if 'status' in data:
            request_data = request_doc.to_dict()
            user_id = request_data.get('user_id')
            
            if user_id:
                user_ref = db.collection('users').document(user_id)
                user_doc = user_ref.get()
                
                if user_doc.exists:
                    user_data = user_doc.to_dict()
                    request_history = user_data.get('request_history', [])
                    
                    # Find and update the request in history
                    for i, req in enumerate(request_history):
                        if req.get('request_id') == request_id:
                            request_history[i]['status'] = data['status']
                            user_ref.update({'request_history': request_history})
                            break
        
        return True
    except Exception as e:
        print(f"Error in update_blood_request: {str(e)}")
        return False

# Donor Functions
def get_available_donors(blood_group=None):
    """Get available donors with optional blood group filter."""
    try:
        db = get_firestore_db()
        query = db.collection('users').where('role', '==', 'donor').where('available', '==', True)
        
        if blood_group:
            query = query.where('blood_group', '==', blood_group)
        
        donors = query.get()
        donor_list = []
        
        for doc in donors:
            donor_data = doc.to_dict()
            donor_data['id'] = doc.id  # Add document ID for reference
            donor_list.append(donor_data)
        
        return donor_list
    except Exception as e:
        print(f"Error in get_available_donors: {str(e)}")
        return []

def record_donation(donor_id, donation_data):
    """Record a blood donation."""
    try:
        db = get_firestore_db()
        donation_data['created_at'] = get_server_timestamp()
        
        # Get donor's current data
        donor_ref = db.collection('users').document(donor_id)
        donor_doc = donor_ref.get()
        
        if not donor_doc.exists:
            return False
        
        donor_data = donor_doc.to_dict()
        donation_history = donor_data.get('donation_history', [])
        donation_history.append(donation_data)
        
        # Update donor's donation history
        donor_ref.update({'donation_history': donation_history})
        
        # Update blood inventory
        blood_group = donation_data['blood_group']
        units = donation_data['units']
        
        inventory_ref = db.collection('inventory').document('blood_inventory')
        inventory_doc = inventory_ref.get()
        
        if inventory_doc.exists:
            inventory_data = inventory_doc.to_dict()
            
            if blood_group in inventory_data:
                current_units = inventory_data.get(blood_group, 0)
                inventory_data[blood_group] = current_units + units
            else:
                inventory_data[blood_group] = units
            
            inventory_data['last_updated'] = get_server_timestamp()
            inventory_ref.update(inventory_data)
        else:
            inventory_ref.set({
                blood_group: units,
                'last_updated': get_server_timestamp()
            })
        
        return True
    except Exception as e:
        print(f"Error in record_donation: {str(e)}")
        return False

# Notification Functions
def create_notification(user_id, notification_data):
    """Create a notification for a user."""
    try:
        db = get_firestore_db()
        notification_data['created_at'] = get_server_timestamp()
        notification_data['read'] = False
        
        notification_ref = db.collection('users').document(user_id).collection('notifications').document()
        notification_data['id'] = notification_ref.id
        notification_ref.set(notification_data)
        
        return notification_ref.id
    except Exception as e:
        print(f"Error in create_notification: {str(e)}")
        raise

def get_notifications(user_id):
    """Get notifications for a user."""
    try:
        db = get_firestore_db()
        notifications_ref = db.collection('users').document(user_id).collection('notifications').order_by('created_at', 'desc')
        notifications = notifications_ref.get()
        
        result = []
        for doc in notifications:
            notification_data = doc.to_dict()
            # Convert server timestamp to string format if needed
            if notification_data.get('created_at'):
                if isinstance(notification_data['created_at'], datetime):
                    notification_data['created_at'] = notification_data['created_at'].strftime('%Y-%m-%d %H:%M:%S')
            result.append(notification_data)
        
        return result
    except Exception as e:
        print(f"Error in get_notifications: {str(e)}")
        return []

def mark_notification_as_read(user_id, notification_id):
    """Mark a notification as read."""
    try:
        db = get_firestore_db()
        db.collection('users').document(user_id).collection('notifications').document(notification_id).update({
            'read': True
        })
        return True
    except Exception as e:
        print(f"Error in mark_notification_as_read: {str(e)}")
        return False

# Admin Functions
def get_all_users(role=None):
    """Get all users with optional role filter."""
    try:
        db = get_firestore_db()
        if role:
            users_ref = db.collection('users').where('role', '==', role)
        else:
            users_ref = db.collection('users')
        
        users = users_ref.get()
        user_list = []
        
        for doc in users:
            user_data = doc.to_dict()
            user_data['id'] = doc.id  # Add document ID for reference
            user_list.append(user_data)
        
        return user_list
    except Exception as e:
        print(f"Error in get_all_users: {str(e)}")
        return []

def get_donation_stats():
    """Get donation statistics."""
    try:
        db = get_firestore_db()
        users_ref = db.collection('users').where('role', '==', 'donor')
        users = users_ref.get()
        
        total_donations = 0
        donations_by_group = {
            "A+": 0, "A-": 0, "B+": 0, "B-": 0, 
            "AB+": 0, "AB-": 0, "O+": 0, "O-": 0
        }
        
        for doc in users:
            user_data = doc.to_dict()
            donation_history = user_data.get('donation_history', [])
            
            for donation in donation_history:
                total_donations += 1
                blood_group = donation.get('blood_group')
                if blood_group in donations_by_group:
                    donations_by_group[blood_group] += 1
        
        return {
            'total_donations': total_donations,
            'donations_by_group': donations_by_group
        }
    except Exception as e:
        print(f"Error in get_donation_stats: {str(e)}")
        return {'total_donations': 0, 'donations_by_group': {}}

def get_request_stats():
    """Get request statistics."""
    try:
        db = get_firestore_db()
        requests_ref = db.collection('blood_requests')
        requests = requests_ref.get()
        
        total_requests = 0
        pending_requests = 0
        approved_requests = 0
        completed_requests = 0
        canceled_requests = 0
        
        requests_by_group = {
            "A+": 0, "A-": 0, "B+": 0, "B-": 0, 
            "AB+": 0, "AB-": 0, "O+": 0, "O-": 0
        }
        
        for doc in requests:
            request_data = doc.to_dict()
            total_requests += 1
            
            status = request_data.get('status')
            if status == 'pending':
                pending_requests += 1
            elif status == 'approved':
                approved_requests += 1
            elif status == 'completed':
                completed_requests += 1
            elif status == 'cancelled':
                canceled_requests += 1
            
            blood_group = request_data.get('blood_group')
            if blood_group in requests_by_group:
                requests_by_group[blood_group] += 1
        
        return {
            'total_requests': total_requests,
            'pending_requests': pending_requests,
            'approved_requests': approved_requests,
            'completed_requests': completed_requests,
            'canceled_requests': canceled_requests,
            'requests_by_group': requests_by_group
        }
    except Exception as e:
        print(f"Error in get_request_stats: {str(e)}")
        return {
            'total_requests': 0,
            'pending_requests': 0,
            'approved_requests': 0,
            'completed_requests': 0,
            'canceled_requests': 0,
            'requests_by_group': {}
        }
