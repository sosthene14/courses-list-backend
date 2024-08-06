import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

class EmailSender:
    def __init__(self, email_from: str, sender_password: str, email_to: list[str], email_subject: str,
                 email_message: str):
        self.email_from = email_from
        self.email_to = email_to
        self.sender_password = sender_password
        self.email_subject = email_subject
        self.email_message = email_message

    def sendEmail(self):
        message = MIMEMultipart()
        message["From"] = self.email_from
        message["Subject"] = self.email_subject
        message.attach(MIMEText(self.email_message, "html", "utf-8"))

        smtp_server = "smtp.gmail.com"
        smtp_port = 587
        try:
            with smtplib.SMTP(smtp_server, smtp_port) as server:
                server.starttls()  # Activer le chiffrement TLS
                server.login(self.email_from, self.sender_password)
                for destinataire_email in self.email_to:
                    server.sendmail(self.email_from, destinataire_email, message.as_string())
        except Exception as e:
            print("Erreur :", e)
