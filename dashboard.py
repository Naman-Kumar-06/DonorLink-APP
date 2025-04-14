import streamlit as st
import pandas as pd
import plotly.express as px
import database
from datetime import datetime

def show_notifications(user_id):
    """Display notifications for the current user"""
    with st.expander("📬 Notifications"):
        notifications = database.get_notifications(user_id)
        
        if not notifications:
            st.info("No notifications yet.")
        else:
            for notification in notifications:
                col1, col2 = st.columns([5, 1])
                
                with col1:
                    if notification.get('read', False):
                        st.write(notification.get('message', 'No message'))
                    else:
                        st.markdown(f"**{notification.get('message', 'No message')}**")
                    
                    # Format the timestamp if it exists
                    created_at = notification.get('created_at')
                    if created_at:
                        if isinstance(created_at, str):
                            timestamp = created_at
                        else:
                            try:
                                timestamp = created_at.strftime("%Y-%m-%d %H:%M:%S")
                            except:
                                timestamp = "Unknown date"
                        st.caption(f"Received: {timestamp}")
                    else:
                        st.caption("Received: Unknown date")
                
                with col2:
                    if not notification.get('read', False):
                        if st.button("Mark Read", key=f"read_{notification.get('id')}"):
                            database.mark_notification_as_read(user_id, notification.get('id'))
                            st.rerun()
                
                st.divider()

def show_blood_inventory(key_suffix=""):
    """Display the current blood inventory
    
    Args:
        key_suffix (str): A unique suffix for chart keys to avoid duplicates
    """
    inventory = database.get_blood_inventory()
    
    if not inventory:
        st.warning("No blood inventory data available.")
        return
    
    # Convert to DataFrame for better display
    inventory_df = pd.DataFrame({
        'Blood Group': list(inventory.keys()),
        'Units Available': list(inventory.values())
    })
    
    # Display as a bar chart with Streamlit's theme colors
    fig = px.bar(
        inventory_df, 
        x='Blood Group', 
        y='Units Available',
        color='Blood Group',
        title='Current Blood Inventory',
        color_discrete_sequence=px.colors.qualitative.Set1
    )
    
    # Customize layout
    fig.update_layout(
        xaxis_title="Blood Group",
        yaxis_title="Units Available",
        legend_title="Blood Group"
    )
    
    # Use a unique key for the chart
    st.plotly_chart(fig, use_container_width=True, key=f"blood_inventory_chart_{key_suffix}")
    
    # Also show as a table with a unique key
    st.dataframe(inventory_df, use_container_width=True, hide_index=True, key=f"blood_inventory_table_{key_suffix}")

def display_blood_requests(status=None, user_id=None, role=None):
    """Display blood requests with optional filtering"""
    
    # Get blood requests based on filters
    if user_id and role == 'receiver':
        # For receivers, get only their own requests
        all_requests = database.get_blood_requests()
        requests = [r for r in all_requests if r.get('user_id') == user_id]
    else:
        # For admins or donors, get all or filtered by status
        requests = database.get_blood_requests(status)
    
    if not requests:
        st.info("No blood requests found.")
        return
    
    # Convert to DataFrame for better display
    request_data = []
    for req in requests:
        # Format the timestamp if it exists
        created_at = req.get('created_at')
        if created_at:
            if isinstance(created_at, str):
                timestamp = created_at
            elif isinstance(created_at, datetime):
                timestamp = created_at.strftime("%Y-%m-%d %H:%M:%S")
            else:
                timestamp = "Unknown date"
        else:
            timestamp = "Unknown date"
        
        request_data.append({
            'Request ID': req.get('request_id', 'Unknown'),
            'Blood Group': req.get('blood_group', 'Unknown'),
            'Units': req.get('units', 0),
            'Urgency': req.get('urgency', 'Normal'),
            'Location': req.get('location', 'Unknown'),
            'Status': req.get('status', 'Unknown'),
            'Requested By': req.get('requester_name', 'Unknown'),
            'Request Date': timestamp,
            'Full Data': req  # Store full data for actions
        })
    
    requests_df = pd.DataFrame(request_data)
    
    # Display as table
    if 'Full Data' in requests_df.columns:
        display_df = requests_df.drop(columns=['Full Data'])
    else:
        display_df = requests_df
    
    st.dataframe(display_df, use_container_width=True, hide_index=True)
    
    return requests_df
