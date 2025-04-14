import streamlit as st
import pandas as pd
import plotly.express as px
import database
import dashboard
from utils import display_message
from datetime import datetime

def show_admin_dashboard():
    """Display the admin dashboard"""
    st.title("🩸 Admin Dashboard")
    
    # Show notifications
    if st.session_state.user_id:
        dashboard.show_notifications(st.session_state.user_id)
    
    # Create tabs for different sections
    tabs = st.tabs(["Overview", "Inventory", "Blood Requests", "Donors", "Receivers", "Reports"])
    
    # Overview Tab
    with tabs[0]:
        show_overview()
    
    # Inventory Tab
    with tabs[1]:
        show_inventory_management()
    
    # Blood Requests Tab
    with tabs[2]:
        show_blood_request_management()
    
    # Donors Tab
    with tabs[3]:
        show_donor_management()
    
    # Receivers Tab
    with tabs[4]:
        show_receiver_management()
    
    # Reports Tab
    with tabs[5]:
        show_reports()

def show_overview():
    """Display the overview dashboard with key metrics"""
    st.header("System Overview")
    
    # Get statistics
    inventory = database.get_blood_inventory()
    donor_count = len(database.get_all_users(role="donor"))
    receiver_count = len(database.get_all_users(role="receiver"))
    
    # Get request statistics
    request_stats = database.get_request_stats()
    
    # Create metrics
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Registered Donors", donor_count)
    
    with col2:
        st.metric("Registered Receivers", receiver_count)
    
    with col3:
        st.metric("Total Requests", request_stats.get('total_requests', 0))
    
    with col4:
        total_blood_units = sum(inventory.values()) if inventory else 0
        st.metric("Total Blood Units", total_blood_units)
    
    # Display pending requests
    st.subheader("Pending Blood Requests")
    pending_requests = database.get_blood_requests(status="pending")
    
    if not pending_requests:
        st.info("No pending blood requests.")
    else:
        # Convert to DataFrame for display
        df_data = []
        for req in pending_requests:
            df_data.append({
                'Request ID': req.get('request_id', 'Unknown'),
                'Blood Group': req.get('blood_group', 'Unknown'),
                'Units': req.get('units', 0),
                'Urgency': req.get('urgency', 'Normal'),
                'Requester': req.get('requester_name', 'Unknown'),
                'Organization': req.get('organization', 'Unknown'),
                'Created At': req.get('created_at', 'Unknown date')
            })
        
        if df_data:
            df = pd.DataFrame(df_data)
            st.dataframe(df, use_container_width=True, hide_index=True)
    
    # Display blood inventory overview
    st.subheader("Blood Inventory Overview")
    dashboard.show_blood_inventory(key_suffix="overview")

def show_inventory_management():
    """Display and manage blood inventory"""
    st.header("Blood Inventory Management")
    
    # Get current inventory
    inventory = database.get_blood_inventory()
    
    # Display current inventory
    st.subheader("Current Inventory")
    dashboard.show_blood_inventory(key_suffix="management")
    
    # Form to update inventory
    st.subheader("Update Inventory")
    
    with st.form(key="update_inventory_form"):
        blood_group = st.selectbox("Blood Group", 
                                   options=["A+", "A-", "B+", "B-", "AB+", "AB-", "O+", "O-"])
        
        current_units = inventory.get(blood_group, 0)
        st.write(f"Current units: {current_units}")
        
        action = st.radio("Action", options=["Add", "Remove"])
        units = st.number_input("Units", min_value=1, max_value=100, value=1)
        
        reason = st.text_area("Reason for update")
        
        submit_button = st.form_submit_button(label="Update Inventory")
        
        if submit_button:
            if action == "Remove" and units > current_units:
                st.error(f"Cannot remove {units} units. Only {current_units} units available.")
            else:
                try:
                    # Calculate new value
                    new_units = current_units + units if action == "Add" else current_units - units
                    
                    # Update inventory
                    update_data = {blood_group: new_units}
                    result = database.update_blood_inventory(update_data)
                    
                    if result:
                        display_message("success", f"Inventory updated successfully! {blood_group}: {current_units} → {new_units}")
                        
                        # Create a record of this transaction (in a real app, you'd store this in Firestore)
                        transaction_record = {
                            'blood_group': blood_group,
                            'action': action,
                            'units': units,
                            'previous_units': current_units,
                            'new_units': new_units,
                            'reason': reason,
                            'updated_by': st.session_state.user_id,
                            'timestamp': datetime.now().isoformat()
                        }
                        print(f"Inventory transaction: {transaction_record}")
                        
                        # Refresh the page to show updated inventory
                        st.rerun()
                    else:
                        display_message("error", "Failed to update inventory.")
                except Exception as e:
                    display_message("error", f"Error updating inventory: {str(e)}")

def show_blood_request_management():
    """Display and manage blood requests"""
    st.header("Blood Request Management")
    
    # Create tabs for different request statuses
    tab1, tab2, tab3, tab4 = st.tabs(["Pending", "Approved", "Completed", "Cancelled"])
    
    # Pending Requests Tab
    with tab1:
        st.subheader("Pending Requests")
        pending_df = dashboard.display_blood_requests(status="pending")
        
        if pending_df is not None and not pending_df.empty:
            st.subheader("Process Request")
            
            # Create selection for processing
            request_options = {row['Request ID']: f"{row['Blood Group']} - {row['Units']} units - {row['Requested By']}" 
                            for _, row in pending_df.iterrows()}
            
            selected_request_id = st.selectbox("Select request to process:", 
                                            options=list(request_options.keys()),
                                            format_func=lambda x: request_options[x])
            
            # Get selected request details
            selected_request = None
            for _, row in pending_df.iterrows():
                if row['Request ID'] == selected_request_id:
                    selected_request = row['Full Data']
                    break
            
            if selected_request:
                col1, col2 = st.columns(2)
                
                with col1:
                    # Check if we have enough inventory
                    inventory = database.get_blood_inventory()
                    blood_group = selected_request.get('blood_group')
                    units_requested = selected_request.get('units', 0)
                    units_available = inventory.get(blood_group, 0)
                    
                    st.write(f"Blood Group: {blood_group}")
                    st.write(f"Units Requested: {units_requested}")
                    st.write(f"Units Available: {units_available}")
                    
                    if units_available < units_requested:
                        st.warning(f"⚠️ Insufficient inventory. Only {units_available} units available.")
                
                with col2:
                    st.write(f"Requester: {selected_request.get('requester_name')}")
                    st.write(f"Organization: {selected_request.get('organization', 'N/A')}")
                    st.write(f"Urgency: {selected_request.get('urgency', 'Normal')}")
                
                admin_notes = st.text_area("Admin Notes", placeholder="Add any notes about this request")
                
                col1, col2, col3 = st.columns(3)
                
                with col1:
                    if st.button("Approve Request", use_container_width=True):
                        try:
                            # Update request status
                            database.update_blood_request(selected_request_id, {
                                'status': 'approved',
                                'admin_notes': admin_notes,
                                'processed_by': st.session_state.user_id,
                                'processed_at': datetime.now().isoformat()
                            })
                            
                            # Notify requester
                            notification_data = {
                                'message': f"Your blood request for {units_requested} units of {blood_group} has been approved.",
                                'type': 'request_approved',
                                'request_id': selected_request_id
                            }
                            database.create_notification(selected_request.get('user_id'), notification_data)
                            
                            display_message("success", "Request approved successfully!")
                            st.rerun()
                        except Exception as e:
                            display_message("error", f"Failed to approve request: {str(e)}")
                
                with col2:
                    if st.button("Complete Request", use_container_width=True):
                        if units_available < units_requested:
                            st.error("Cannot complete request due to insufficient inventory.")
                        else:
                            try:
                                # Update request status
                                database.update_blood_request(selected_request_id, {
                                    'status': 'completed',
                                    'admin_notes': admin_notes,
                                    'processed_by': st.session_state.user_id,
                                    'processed_at': datetime.now().isoformat()
                                })
                                
                                # Update inventory
                                new_units = units_available - units_requested
                                database.update_blood_inventory({blood_group: new_units})
                                
                                # Notify requester
                                notification_data = {
                                    'message': f"Your blood request for {units_requested} units of {blood_group} has been completed.",
                                    'type': 'request_completed',
                                    'request_id': selected_request_id
                                }
                                database.create_notification(selected_request.get('user_id'), notification_data)
                                
                                display_message("success", "Request completed successfully! Inventory updated.")
                                st.rerun()
                            except Exception as e:
                                display_message("error", f"Failed to complete request: {str(e)}")
                
                with col3:
                    if st.button("Reject Request", use_container_width=True):
                        try:
                            # Update request status
                            database.update_blood_request(selected_request_id, {
                                'status': 'rejected',
                                'admin_notes': admin_notes,
                                'processed_by': st.session_state.user_id,
                                'processed_at': datetime.now().isoformat()
                            })
                            
                            # Notify requester
                            notification_data = {
                                'message': f"Your blood request for {units_requested} units of {blood_group} has been rejected. Reason: {admin_notes if admin_notes else 'No reason provided'}",
                                'type': 'request_rejected',
                                'request_id': selected_request_id
                            }
                            database.create_notification(selected_request.get('user_id'), notification_data)
                            
                            display_message("success", "Request rejected.")
                            st.rerun()
                        except Exception as e:
                            display_message("error", f"Failed to reject request: {str(e)}")
    
    # Approved Requests Tab
    with tab2:
        st.subheader("Approved Requests")
        dashboard.display_blood_requests(status="approved")
    
    # Completed Requests Tab
    with tab3:
        st.subheader("Completed Requests")
        dashboard.display_blood_requests(status="completed")
    
    # Cancelled Requests Tab
    with tab4:
        st.subheader("Cancelled/Rejected Requests")
        cancelled_df = dashboard.display_blood_requests(status="cancelled")
        rejected_df = dashboard.display_blood_requests(status="rejected")

def show_donor_management():
    """Display and manage donors"""
    st.header("Donor Management")
    
    # Get all donors
    donors = database.get_all_users(role="donor")
    
    if not donors:
        st.info("No donors registered yet.")
        return
    
    # Display donors in a dataframe
    donor_data = []
    for donor in donors:
        donor_data.append({
            'ID': donor.get('id', 'Unknown'),
            'Name': donor.get('name', 'Unknown'),
            'Blood Group': donor.get('blood_group', 'Unknown'),
            'Phone': donor.get('phone', 'Unknown'),
            'City': donor.get('city', 'Unknown'),
            'Available': '✅' if donor.get('available', False) else '❌',
            'Donations': len(donor.get('donation_history', [])),
            'Full Data': donor
        })
    
    if donor_data:
        df = pd.DataFrame(donor_data)
        display_df = df.drop(columns=['Full Data', 'ID'])
        st.dataframe(display_df, use_container_width=True, hide_index=True)
    
    # Donor details and actions
    st.subheader("Donor Details")
    
    if donor_data:
        # Create selection for viewing donor details
        donor_options = {donor['ID']: f"{donor['Name']} - {donor['Blood Group']}" for donor in donor_data}
        selected_donor_id = st.selectbox("Select donor:", 
                                       options=list(donor_options.keys()),
                                       format_func=lambda x: donor_options[x])
        
        # Get selected donor details
        selected_donor = None
        for donor in donor_data:
            if donor['ID'] == selected_donor_id:
                selected_donor = donor['Full Data']
                break
        
        if selected_donor:
            col1, col2 = st.columns(2)
            
            with col1:
                st.write("**Personal Information**")
                st.write(f"Name: {selected_donor.get('name', 'Unknown')}")
                st.write(f"Email: {selected_donor.get('email', 'Unknown')}")
                st.write(f"Phone: {selected_donor.get('phone', 'Unknown')}")
                st.write(f"Address: {selected_donor.get('address', 'Unknown')}")
                st.write(f"City: {selected_donor.get('city', 'Unknown')}")
            
            with col2:
                st.write("**Donation Status**")
                st.write(f"Blood Group: {selected_donor.get('blood_group', 'Unknown')}")
                st.write(f"Available for donation: {'Yes' if selected_donor.get('available', False) else 'No'}")
                donation_history = selected_donor.get('donation_history', [])
                st.write(f"Total donations: {len(donation_history)}")
            
            # Donation history
            st.write("**Donation History**")
            
            if not donation_history:
                st.info("No donation history available.")
            else:
                history_data = []
                for donation in donation_history:
                    history_data.append({
                        'Date': donation.get('donation_date', 'Unknown'),
                        'Blood Group': donation.get('blood_group', 'Unknown'),
                        'Units': donation.get('units', 0),
                        'Location': donation.get('location', 'Unknown'),
                        'Notes': donation.get('notes', '')
                    })
                
                history_df = pd.DataFrame(history_data)
                st.dataframe(history_df, use_container_width=True, hide_index=True)
            
            # Send notification to donor
            st.write("**Send Notification**")
            
            with st.form(key=f"notify_donor_{selected_donor_id}"):
                message = st.text_area("Message", placeholder="Enter message for the donor")
                submit = st.form_submit_button("Send Notification")
                
                if submit and message:
                    try:
                        notification_data = {
                            'message': message,
                            'type': 'admin_message'
                        }
                        database.create_notification(selected_donor_id, notification_data)
                        display_message("success", "Notification sent successfully!")
                    except Exception as e:
                        display_message("error", f"Failed to send notification: {str(e)}")

def show_receiver_management():
    """Display and manage receivers"""
    st.header("Receiver Management")
    
    # Get all receivers
    receivers = database.get_all_users(role="receiver")
    
    if not receivers:
        st.info("No receivers registered yet.")
        return
    
    # Display receivers in a dataframe
    receiver_data = []
    for receiver in receivers:
        receiver_data.append({
            'ID': receiver.get('id', 'Unknown'),
            'Name': receiver.get('name', 'Unknown'),
            'Organization': receiver.get('organization', 'Unknown'),
            'Phone': receiver.get('phone', 'Unknown'),
            'City': receiver.get('city', 'Unknown'),
            'Requests': len(receiver.get('request_history', [])),
            'Full Data': receiver
        })
    
    if receiver_data:
        df = pd.DataFrame(receiver_data)
        display_df = df.drop(columns=['Full Data', 'ID'])
        st.dataframe(display_df, use_container_width=True, hide_index=True)
    
    # Receiver details and actions
    st.subheader("Receiver Details")
    
    if receiver_data:
        # Create selection for viewing receiver details
        receiver_options = {receiver['ID']: f"{receiver['Name']} - {receiver['Organization']}" for receiver in receiver_data}
        selected_receiver_id = st.selectbox("Select receiver:", 
                                          options=list(receiver_options.keys()),
                                          format_func=lambda x: receiver_options[x])
        
        # Get selected receiver details
        selected_receiver = None
        for receiver in receiver_data:
            if receiver['ID'] == selected_receiver_id:
                selected_receiver = receiver['Full Data']
                break
        
        if selected_receiver:
            col1, col2 = st.columns(2)
            
            with col1:
                st.write("**Organization Information**")
                st.write(f"Organization: {selected_receiver.get('organization', 'Unknown')}")
                st.write(f"Contact Person: {selected_receiver.get('name', 'Unknown')}")
                st.write(f"Email: {selected_receiver.get('email', 'Unknown')}")
                st.write(f"Phone: {selected_receiver.get('phone', 'Unknown')}")
            
            with col2:
                st.write("**Address Information**")
                st.write(f"Address: {selected_receiver.get('address', 'Unknown')}")
                st.write(f"City: {selected_receiver.get('city', 'Unknown')}")
                request_history = selected_receiver.get('request_history', [])
                st.write(f"Total requests: {len(request_history)}")
            
            # Request history
            st.write("**Request History**")
            
            if not request_history:
                st.info("No request history available.")
            else:
                history_data = []
                for request in request_history:
                    history_data.append({
                        'Request ID': request.get('request_id', 'Unknown'),
                        'Date': request.get('created_at', 'Unknown'),
                        'Blood Group': request.get('blood_group', 'Unknown'),
                        'Units': request.get('units', 0),
                        'Status': request.get('status', 'Unknown')
                    })
                
                history_df = pd.DataFrame(history_data)
                st.dataframe(history_df, use_container_width=True, hide_index=True)
            
            # Send notification to receiver
            st.write("**Send Notification**")
            
            with st.form(key=f"notify_receiver_{selected_receiver_id}"):
                message = st.text_area("Message", placeholder="Enter message for the receiver")
                submit = st.form_submit_button("Send Notification")
                
                if submit and message:
                    try:
                        notification_data = {
                            'message': message,
                            'type': 'admin_message'
                        }
                        database.create_notification(selected_receiver_id, notification_data)
                        display_message("success", "Notification sent successfully!")
                    except Exception as e:
                        display_message("error", f"Failed to send notification: {str(e)}")

def show_reports():
    """Display system reports and analytics"""
    st.header("Reports and Analytics")
    
    # Display tabs for different reports
    tab1, tab2, tab3 = st.tabs(["Donation Statistics", "Request Statistics", "Inventory Analysis"])
    
    # Donation Statistics Tab
    with tab1:
        st.subheader("Donation Statistics")
        
        donation_stats = database.get_donation_stats()
        total_donations = donation_stats.get('total_donations', 0)
        donations_by_group = donation_stats.get('donations_by_group', {})
        
        st.metric("Total Donations", total_donations)
        
        if donations_by_group:
            # Create dataframe for chart
            df = pd.DataFrame({
                'Blood Group': list(donations_by_group.keys()),
                'Donations': list(donations_by_group.values())
            })
            
            # Create pie chart
            fig = px.pie(df, values='Donations', names='Blood Group', 
                         title='Donations by Blood Group',
                         color_discrete_sequence=px.colors.sequential.RdBu)
            st.plotly_chart(fig, use_container_width=True)
    
    # Request Statistics Tab
    with tab2:
        st.subheader("Request Statistics")
        
        request_stats = database.get_request_stats()
        
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric("Total Requests", request_stats.get('total_requests', 0))
        
        with col2:
            st.metric("Pending", request_stats.get('pending_requests', 0))
        
        with col3:
            st.metric("Approved", request_stats.get('approved_requests', 0))
        
        with col4:
            st.metric("Completed", request_stats.get('completed_requests', 0))
        
        requests_by_group = request_stats.get('requests_by_group', {})
        
        if requests_by_group:
            # Create dataframe for chart
            df = pd.DataFrame({
                'Blood Group': list(requests_by_group.keys()),
                'Requests': list(requests_by_group.values())
            })
            
            # Create bar chart
            fig = px.bar(df, x='Blood Group', y='Requests', 
                        title='Requests by Blood Group',
                        color='Blood Group')
            st.plotly_chart(fig, use_container_width=True)
    
    # Inventory Analysis Tab
    with tab3:
        st.subheader("Inventory Analysis")
        
        # Get current inventory
        inventory = database.get_blood_inventory()
        
        if inventory:
            # Create dataframe for inventory
            df = pd.DataFrame({
                'Blood Group': list(inventory.keys()),
                'Units Available': list(inventory.values())
            })
            
            # Create a gauge chart for each blood group
            for blood_group in inventory:
                value = inventory[blood_group]
                max_value = 100  # Assuming 100 is the maximum we'd expect
                
                # Determine status color
                if value < 5:
                    color = "red"
                elif value < 20:
                    color = "orange"
                else:
                    color = "green"
                
                col1, col2 = st.columns([1, 3])
                
                with col1:
                    st.metric(f"{blood_group}", value)
                
                with col2:
                    # Create a simple progress bar
                    progress = st.progress(min(value / max_value, 1.0))
                    
                    # Add status text
                    if value < 5:
                        st.write("⚠️ **Critical level!** Immediate donation needed.")
                    elif value < 20:
                        st.write("⚠️ **Low inventory.** Donation recommended.")
                    else:
                        st.write("✅ **Good inventory level.**")
