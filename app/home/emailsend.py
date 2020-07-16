import smtplib, ssl
from smtplib import SMTP 
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from threading import Thread

port = 465  # For SSL
smtp_server = "smtp.gmail.com"
sender_email = "topulentt@gmail.com"  # Enter your address
password = 'Silver12!'

def threading(f):
    def wrapper(*args, **kwargs):
        thr = Thread(target=f, args=args, kwargs=kwargs)
        thr.start()
    return wrapper

@threading
def send_forgotpass__mail(email,htmll):
    receiver_email = email  # Enter receiver address

    message = MIMEMultipart("alternative")
    message["Subject"] = "The Opulent Group - Forgot Password?"
    message["From"] = sender_email
    message["To"] = receiver_email

    part2 = MIMEText(htmll, "html")

    message.attach(part2)
    
    context = ssl.create_default_context()
    with smtplib.SMTP_SSL(smtp_server, port, context=context) as server:
        server.login(sender_email, password)
        server.sendmail(sender_email, receiver_email, message.as_string())

# if __name__ == "__main__":
#     send_mail('groundbuster2@gmail.com')