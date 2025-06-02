import smtplib
from email.message import EmailMessage
from config import Config


class Mailer:
    def __init__(self):
        self.smtp_server = Config.SMTP_SERVER
        self.smtp_port = Config.SMTP_PORT
        self.username = Config.SMTP_USERNAME
        self.password = Config.SMTP_PASSWORD
        self.use_tls = Config.SMTP_USE_TLS

    def send_mail(self, subject: str, body: str, from_addr: str, to_addrs: list, html: bool = False):
        msg = EmailMessage()
        msg['Subject'] = subject
        msg['From'] = from_addr
        msg['To'] = to_addrs

        if html:
            msg.set_content(body)
            msg.add_alternative(body, subtype='html')
        else:
            msg.set_content(body)

        with smtplib.SMTP(self.smtp_server, self.smtp_port) as server:
            if self.use_tls:
                server.starttls()
            server.login(self.username, self.password)
            server.send_message(msg)
            print(f"Email sent successfully to {to_addrs}")
        


if __name__ == "__main__":
    mailer = Mailer()

    subject = "Test Email from Python"
    body = "Hello,\n\nThis is a test email sent from Python using SMTP with .env configuration.\n\nCheers!"
    from_address = mailer.username
    recipients = "wissmahasneh@gmail.com"
    mailer.send_mail(subject, body, from_address, recipients)