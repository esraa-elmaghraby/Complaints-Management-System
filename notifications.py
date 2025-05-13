import streamlit as st
import time

def display_notifications():
    if "notifications" in st.session_state and len(st.session_state.notifications) > 0:
        for notification in st.session_state.notifications:
            notification_expander = st.expander(notification, expanded=True)
            with notification_expander:
                st.write(notification) 
            time.sleep(2)
            st.session_state.notifications.remove(notification)
