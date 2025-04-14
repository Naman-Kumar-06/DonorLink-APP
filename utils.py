import streamlit as st
import re
from datetime import datetime

def validate_email(email):
    """Validate email format"""
    pattern = r'^[\w\.-]+@[\w\.-]+\.\w+$'
    return re.match(pattern, email) is not None

def validate_password(password):
    """Validate password length"""
    return len(password) >= 6

def display_message(type, message):
    """Display message with specified type (success, info, warning, error)"""
    if type == "success":
        st.success(message)
    elif type == "info":
        st.info(message)
    elif type == "warning":
        st.warning(message)
    elif type == "error":
        st.error(message)

def format_date(date_str):
    """Format date string for display"""
    if not date_str:
        return "Unknown date"
    
    try:
        # Try to parse the date string into a datetime object
        if isinstance(date_str, str):
            date_formats = [
                "%Y-%m-%d",
                "%Y-%m-%d %H:%M:%S",
                "%d/%m/%Y",
                "%m/%d/%Y"
            ]
            
            for fmt in date_formats:
                try:
                    dt = datetime.strptime(date_str, fmt)
                    return dt.strftime("%d %b %Y")
                except ValueError:
                    continue
                
            # If no format worked, return the original string
            return date_str
        elif isinstance(date_str, datetime):
            return date_str.strftime("%d %b %Y")
        else:
            return str(date_str)
    except:
        return date_str
