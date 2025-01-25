from dotenv import load_dotenv
import os
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

load_dotenv()

USERNAME = os.getenv("EMAIL_SENDER")
PASSWORD = os.getenv("EMAIL_PASSWORD")
RECEIVER = os.getenv("EMAIL_RECEIVER")

def send_email(subject, html_content, sender=USERNAME, receiver=RECEIVER):
    # Crear un missatge multipart per al correu
    new_message = MIMEMultipart("alternative")
    new_message["From"] = sender
    new_message["To"] = receiver
    new_message["Subject"] = subject

    # Afegir contingut HTML
    html_part = MIMEText(html_content, "html")
    new_message.attach(html_part)

    try:
        # Connexió amb el servidor SMTP de Gmail
        with smtplib.SMTP("smtp.gmail.com", 587) as connection:
            connection.starttls()  # Iniciar connexió segura
            connection.login(USERNAME, PASSWORD)
            connection.sendmail(sender, receiver, new_message.as_string())
            print("El correu s'ha enviat correctament!")
    except Exception as e:
        print(f"Error enviant el correu: {e}")

if __name__ == "__main__":
    print("test")