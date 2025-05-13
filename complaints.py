import streamlit as st
import re
from datetime import datetime
from database import load_data
from email_utils import send_email

def is_valid_email(email):
    """Check if the provided email is valid."""
    return re.match(r"[^@]+@[^@]+\.[^@]+", email)

def file_complaint(conn, texts):
    """Handle the process of filing a new complaint."""
    st.title(texts["new_complaint"])
    
    # Get user inputs
    name = st.text_input(texts["name"])
    email = st.text_input(texts["email"])
    category = st.selectbox(texts["complaint_type"], texts["complaint_types"])
    priority = st.selectbox(texts["priority"], texts["priorities"])
    content = st.text_area(texts["complaint_content"])

    # Validate and process submission
    if st.button(texts["submit"]):
        if not name or not email or not content:
            st.error(texts["fill_fields"])
        elif not is_valid_email(email):
            st.error(texts.get("invalid_email", "Please enter a valid email address."))
        else:
            # Insert complaint into database
            cursor = conn.cursor()
            cursor.execute(
                "INSERT INTO complaints (name, email, category, content, priority, status, created_at) VALUES (?, ?, ?, ?, ?, ?, ?)",
                (name, email, category, content, priority, "In Progress", datetime.now().isoformat())
            )
            conn.commit()

            # Send email to user and admin
            send_email(email, name, category, priority, content, language="English")  # Send email in English by default
            st.session_state.notifications.append(texts["complaint_success"])

def manage_complaints(conn, texts):
    """Manage the complaints in the system."""
    st.title(texts["manage_complaints_title"])
    complaints = load_data(conn)

    if complaints:
        for complaint in complaints:
            st.write(f"Complaint ID: {complaint[0]} | Name: {complaint[1]} | Status: {complaint[6]}")

        complaint_id = st.text_input(texts["search_complaint"], "")
        if complaint_id:
            complaint = next((c for c in complaints if str(c[0]) == complaint_id), None)
            if complaint:
                st.write(f"Details: {complaint}")
                status = st.selectbox(texts["new_status"], texts["statuses"])
                if st.button(texts["update_button"]):
                    cursor = conn.cursor()
                    cursor.execute("UPDATE complaints SET status = ? WHERE id = ?", (status, complaint[0]))
                    conn.commit()
                    st.session_state.notifications.append(texts["status_updated"])
            else:
                st.error(texts["no_complaint"])
    else:
        st.write(texts["no_complaints"])
