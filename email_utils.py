import smtplib
from email.message import EmailMessage
import streamlit as st

EMAIL_SENDER = st.secrets["email"]["sender"]
EMAIL_PASSWORD = st.secrets["email"]["password"]
EMAIL_RECEIVER = "esraamaghrabi14@gmail.com"  # Admin email

def send_email(user_email, name, category, priority, content, language="English"):
    try:
        msg = EmailMessage()
        msg['From'] = EMAIL_SENDER
        msg['To'] = user_email

        if language == "Arabic":
            msg['Subject'] = "تم استلام الشكوى"
            msg.set_content(
                f"عزيزي {name},\n\n"
                "تم استلام شكواك بنجاح وهي الآن قيد المراجعة من قبل فريقنا المختص.\n"
                "سنعمل على التعامل معها في أسرع وقت ممكن.\n\n"
                "شكرًا لتواصلك معنا.\n\n"
                "مع أطيب التحيات،\n"
                "فريق إدارة الشكاوى"
            )
        else:
            msg['Subject'] = "Complaint Received"
            msg.set_content(
                f"Dear {name},\n\n"
                "We have received your complaint and it has been submitted to our system.\n"
                "Our team is reviewing it and will take the necessary actions shortly.\n\n"
                "Thank you for contacting us.\n\n"
                "Best regards,\n"
                "Complaints Management Team"
            )

        with smtplib.SMTP_SSL('smtp.gmail.com', 465) as smtp:
            smtp.login(EMAIL_SENDER, EMAIL_PASSWORD)
            smtp.send_message(msg)

        msg_to_admin = EmailMessage()
        msg_to_admin['From'] = EMAIL_SENDER
        msg_to_admin['To'] = EMAIL_RECEIVER
        msg_to_admin['Subject'] = "New Complaint Submitted"
        
        msg_to_admin.set_content(
            f"A new complaint has been submitted to the system:\n\n"
            f"Name: {name}\n"
            f"Email: {user_email}\n"
            f"Category: {category}\n"
            f"Priority: {priority}\n"
            f"Complaint Content:\n{content}\n\n"
            "Please follow up on this complaint via the admin dashboard."
        )

        with smtplib.SMTP_SSL('smtp.gmail.com', 465) as smtp:
            smtp.login(EMAIL_SENDER, EMAIL_PASSWORD)
            smtp.send_message(msg_to_admin)

        print("Emails sent successfully!")

    except Exception as e:
        print(f"Error occurred during sending: {e}")
