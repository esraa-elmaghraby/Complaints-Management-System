import smtplib
from email.message import EmailMessage
import streamlit as st

EMAIL_SENDER = st.secrets["email"]["sender"]
EMAIL_PASSWORD = st.secrets["email"]["password"]
EMAIL_RECEIVER = "esraamaghrabi14@gmail.com"  # Admin email
def send_email(user_email, language="English"):
    try:
        # Construct email message
        msg = EmailMessage()
        msg['From'] = EMAIL_SENDER
        msg['To'] = user_email

        # Define email content based on language
        if language == "Arabic":
            msg['Subject'] = "تم استلام الشكوى"
            msg.set_content(
                "عزيزي المستخدم،\n\n"
                "تم استلام شكواك بنجاح وهي الآن قيد المراجعة من قبل فريقنا المختص.\n"
                "سنعمل على التعامل معها في أسرع وقت ممكن واتخاذ الإجراءات اللازمة.\n\n"
                "شكرًا لتواصلك معنا.\n\n"
                "مع أطيب التحيات،\n"
                "فريق إدارة الشكاوى"
            )
        else:
            msg['Subject'] = "Complaint Received"
            msg.set_content(
                "Dear user,\n\n"
                "We have received your complaint and it has been successfully submitted to our system.\n"
                "Our team is currently reviewing it and will take the necessary steps as soon as possible.\n\n"
                "Thank you for bringing this to our attention.\n\n"
                "Best regards,\n"
                "Complaints Management Team"
            )

        # Send email to user
        with smtplib.SMTP_SSL('smtp.gmail.com', 465) as smtp:
            smtp.login(EMAIL_SENDER, EMAIL_PASSWORD)
            smtp.send_message(msg)

        # Also send a copy to admin
        msg_to_admin = EmailMessage()
        msg_to_admin.set_content(msg.get_payload())
        msg_to_admin['Subject'] = f"[ADMIN COPY] {msg['Subject']}"
        msg_to_admin['From'] = EMAIL_SENDER
        msg_to_admin['To'] = EMAIL_RECEIVER

        with smtplib.SMTP_SSL('smtp.gmail.com', 465) as smtp:
            smtp.login(EMAIL_SENDER, EMAIL_PASSWORD)
            smtp.send_message(msg_to_admin)

        print("Emails sent successfully!")

    except Exception as e:
        print(f"Error occurred during sending: {e}")
