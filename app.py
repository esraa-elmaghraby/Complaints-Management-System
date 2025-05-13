import streamlit as st
import sqlite3
from language import TEXTS
from database import get_db_connection, initialize_db, authenticate, change_password
from complaints import file_complaint, manage_complaints
from notifications import display_notifications
from export import export_data
from analytics import show_analytics

# ...

# Page config
st.set_page_config(page_title="Complaints Management System", layout="wide")

st.markdown("""
    <style>
/* --- Buttons Styling --- */
.stButton > button {
    background-color: #416445;
    color: #FFFFFF !important;
    border: none;
    border-radius: 5px;
    padding: 8px 15px !important; 
    font-size: 14px !important;
    font-weight: bold;
    transition: background-color 0.3s;
    width: 120px !important; 
    text-align: center;
}
.stButton > button:hover {
    background-color: #36543a;
}

/* --- Metric Styling --- */
.stMetric {
    background-color: rgba(103, 45, 180, 0.15);
    border-radius: 15px;
    padding: 20px;
    border: 2px solid rgba(103, 45, 180, 0.5);
    box-shadow: 0 0 10px rgba(103, 45, 180, 0.7);
    backdrop-filter: blur(5px);
    text-align: center;
}
.stMetric > div > div > div > div {
    color: #FFFFFF !important;
    text-shadow: 1px 1px 2px rgba(0, 0, 0, 0.5);
    font-size: 24px;
    font-weight: bold;
}
.stMetric:hover {
    transform: scale(1.03);
    transition: transform 0.3s;
    box-shadow: 0 0 15px rgba(103, 45, 180, 1);
}
</style>
""", unsafe_allow_html=True)


# Initialize session state
if "language" not in st.session_state:
    st.session_state.language = "English"
if "authenticated" not in st.session_state:
    st.session_state.authenticated = False
if "notifications" not in st.session_state:
    st.session_state.notifications = []
if "username" not in st.session_state:
    st.session_state.username = ""

# Show avatar and username at the top of sidebar if logged in
if st.session_state.authenticated:
    st.sidebar.markdown(
        """
        <div style="display: flex; justify-content: center; align-items: center; height: 100%;">
            <img src="https://cdn.pixabay.com/photo/2015/10/05/22/37/blank-profile-picture-973460_1280.png" width="80">
        </div>
        """,
        unsafe_allow_html=True
    )
    st.sidebar.markdown(
        f"<div style='text-align: center; font-weight: bold; margin-bottom: 20px;'>{st.session_state.username}</div>",
        unsafe_allow_html=True
    )

# Language selector
st.sidebar.subheader("Language")
language = st.sidebar.selectbox("Select Language", ["English", "Arabic"], index=0 if st.session_state.language == "English" else 1)
if language != st.session_state.language:
    st.session_state.language = language
    st.rerun()

# Get language texts
texts = TEXTS[st.session_state.language]
from database import create_default_admin

# Database connection
conn = get_db_connection()
initialize_db(conn)
create_default_admin(conn, "admin", "1234")  # باسورد افتراضي

# Admin login UI
if not st.session_state.authenticated:
    admin_login_expanded = st.expander(texts["admin_expander"], expanded=False)
    with admin_login_expanded:
        st.subheader(texts["admin_login"])
        username = st.text_input(texts["username"])
                # تحقق إذا كان المستخدم أول مرة يدخل
        password = st.text_input(texts["password"], type="password")

        if st.button(texts["login_button"]):
            success, first_login = authenticate(username, password, conn)
            if success:
                st.session_state.authenticated = True
                st.session_state.username = username
                st.session_state.first_login = first_login  # تخزين قيمة first_login
                st.success(texts["login_success"])
                st.rerun()
            else:
                st.error(texts["login_error"])


# Sidebar options for sections
sections = [texts["manage_complaints"], texts["analytics"], texts["export_data"]] if st.session_state.authenticated else [texts["file_complaint"]]
section = st.sidebar.selectbox(texts["select_section"], sections)

# زر تغيير الباسورد في الشريط الجانبي
if st.session_state.authenticated:
    if st.sidebar.button("Change Password"):
        st.session_state.change_password_mode = True
        st.sidebar.markdown("---")

# تغيير كلمة المرور (في حال كانت القيمة True في session state)
if "change_password_mode" in st.session_state and st.session_state.change_password_mode:
    # إدخال كلمة المرور القديمة والجديدة
    st.subheader("Change Your Password")
    old_password = st.text_input("Enter old password", type="password")
    new_password = st.text_input("Enter new password", type="password")
    confirm_password = st.text_input("Confirm new password", type="password")

    # شرط التحقق من تطابق الباسورد الجديد مع تأكيده
    if new_password == confirm_password:
        if st.button("Change Password", key="change_password_button_sidebar"):
            success = change_password(st.session_state.username, old_password, new_password, conn)
            if success:
                st.success("Password updated successfully!")
                st.session_state.change_password_mode = False  # إغلاق وضع تغيير الباسورد
                st.rerun()  # إعادة تحميل الصفحة
            else:
                st.error("Old password is incorrect.")
    else:
        st.error("New password and confirmation do not match.")


# زر تسجيل الخروج يظهر فقط إذا كان المستخدم مسجل دخول
if st.session_state.authenticated:
    if st.sidebar.button("Log out", key="log_out_button"):
        st.session_state.authenticated = False
        st.session_state.username = ""
        st.session_state.first_login = False
        st.success("You have been logged out.")
        st.rerun()

# Show buttons only for authenticated admins
if st.session_state.authenticated:
    if "first_login" in st.session_state and st.session_state.first_login:
        st.warning("You are using the default password. Please change it to continue.")
    
        st.subheader("Change Your Password")
        # تأكد من أنك عرفت المتغيرات في مكان سابق
        old_password = st.text_input("Enter old password", type="password")
        new_password = st.text_input("Enter new password", type="password")
        confirm_password = st.text_input("Confirm new password", type="password")
        
        # شرط التحقق من تطابق الباسورد الجديد مع تأكيده
        if new_password == confirm_password:
            if st.button("Change Password", key="change_password_button_main"):
                success = change_password(st.session_state.username, old_password, new_password, conn)
                if success:
                    # تحديث حالة أول مرة دخول (first_login) بعد تغيير الباسورد
                    cursor = conn.cursor()
                    cursor.execute("UPDATE admins SET first_login = 0 WHERE username = ?", (st.session_state.username,))
                    conn.commit()
        
                    st.success("Password updated successfully!")
                    st.session_state.first_login = False  # تحديث في session state
                    st.rerun()  # إعادة تحميل الصفحة
                else:
                    st.error("Old password is incorrect.")


# File complaint (for normal users)
if section == texts["file_complaint"] and not st.session_state.authenticated:
    file_complaint(conn, texts)

# Manage complaints (admin only)
if section == texts["manage_complaints"] and st.session_state.authenticated:
    manage_complaints(conn, texts)

if section == texts["export_data"] and st.session_state.authenticated:
    export_data(conn, texts)

if section == texts["analytics"] and st.session_state.authenticated:
    show_analytics(conn, texts)


# Notifications
display_notifications()
