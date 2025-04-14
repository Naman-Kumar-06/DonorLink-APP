# DonorLink-APP
Cloud Based Blood Donation Management System
Blood Bank Management System: Workflow and Logic Design
System Architecture
The Blood Bank Management System is a Streamlit-based web application that uses a mock Firebase/Firestore implementation for data storage and authentication. Here's a detailed breakdown of its components, workflow, and logic design:

1. Application Entry Point (app.py)
The main application file (app.py) serves as the entry point that:

Initializes the session state
Handles user authentication status
Renders the appropriate dashboard based on user role (admin, donor, receiver)
Manages navigation between different sections
2. Database Layer (database.py)
The database module implements a comprehensive mock database solution that simulates Firebase Firestore:

Mock Classes:

MockFirestore: Simulates the Firestore client interface
MockCollection: Handles collection operations like queries and document access
MockDocument: Represents Firestore documents with methods for CRUD operations
MockQuery: Implements query operations with filtering and ordering
MockAuth: Provides authentication services including login and signup
Data Storage:

Uses Streamlit's session_state to persist data between page reloads
Organizes data into collections (users, blood_requests, inventory)
Supports nested documents and subcollections (e.g., notifications)
Database Functions:

User management (get_user_by_id, update_user_profile)
Blood inventory management (get_blood_inventory, update_blood_inventory)
Blood request handling (create_blood_request, get_blood_requests, update_blood_request)
Notifications (create_notification, get_notifications)
Statistical functions (get_donation_stats, get_request_stats)
3. Authentication Module (auth.py)
Handles user authentication with:

Login form with email/password validation
User registration with role selection (donor or receiver)
Session management to maintain login state
Default test users for admin, donor, and receiver roles
4. Role-Based Dashboards
Admin Dashboard (admin.py)
System overview with key metrics and statistics
Blood inventory management with update capabilities
Blood request approval workflow
Donor management with detailed profiles and notification system
Receiver management with request history
Reports and analytics visualization
Donor Dashboard (donor.py)
Profile management (personal details, blood group, availability)
Donation history tracking
Blood request matching based on blood group
Notification system for donation requests
Receiver Dashboard (receiver.py)
Profile management (organization, contact information)
Blood request form for creating new requests
Request history tracking with status updates
Donor discovery based on blood group compatibility
5. Dashboard Components (dashboard.py)
Provides shared UI components used across different dashboards:

Notification display with read/unread status
Blood inventory visualization with Plotly charts
Blood request tables with filtering capabilities
Date formatting and status indicators
6. Utility Functions (utils.py)
Contains helper functions for:

Input validation (email, password)
Message display with different status types
Date formatting and parsing
Other generic utilities
Data Flow and Business Logic
User Authentication Flow:
User enters email/password
System validates credentials against stored user data
On success, user_id and role are stored in session state
Appropriate dashboard is loaded based on role
Blood Request Process:
Receiver creates a blood request specifying blood group, units, urgency
Request is stored with "pending" status
Admin reviews request and takes action (approve, complete, reject)
System updates inventory when a request is completed
Notifications are sent to the receiver about request status changes
Donation Management:
Donors register and provide blood group and availability info
Admin can view available donors and send notifications
When a donation is recorded, the inventory is updated
Donation history is maintained for each donor
Inventory Management:
System maintains current inventory of all blood groups
Inventory is updated when donations are recorded or requests are fulfilled
Low inventory triggers warnings in the admin dashboard
Inventory visualization provides clear status of available blood
Technical Design Patterns
State Management:
Uses Streamlit's session_state for persistent storage between page reloads
Maintains user authentication state across the application
Stores mock database in session_state as a dictionary structure
Module Organization:
Separation of concerns with dedicated modules for each functionality
Clear interfaces between modules
Reusable components across different dashboard views
Error Handling:
Try-except blocks around database operations
User-friendly error messages with the display_message utility
Form validation for all user inputs
UI/UX Design:
Consistent layout with tabs, expanders, and columns
Role-appropriate interfaces showing only relevant information
Interactive elements with immediate feedback
Data visualization for inventory and statistics
This architecture provides a robust foundation that could easily transition from the current mock implementation to a real Firebase/Firestore backend with minimal changes to the application logic.
