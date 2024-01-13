import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
 
# Email server configuration
#smtp_server = "smtp.gmail.com"  # Use your email provider's SMTP server # gmail
smtp_server = "smtp.gmail.com"
smtp_port = 465  # Use the appropriate port for your email provider
#sender_email = "usfmsbais@gmail.com"  # Your email address
sender_email="usfmsbais@usf.edu"
GMAIL_USERNAME = "usfmsbais"
GMAIL_APP_PASSWORD = "yxhk kmtb oizx kvrk"
receiver_email = "rmuralidharr22@gmail.com"  # Recipient's email address
password = "usfbais2005"  # Your email password
subject = "List Email"  # Email subject
 
chat_list=[]
 
def chat_listpass(self,chat_list):
    self.chat_list=chat_list
 
# body = "This is the body of the text message"
# msg = MIMEText(body)
# msg['Subject'] = "wow"
# msg['From'] = sender_email
# msg['To'] = ', '.join(receiver_email)
# with smtplib.SMTP_SSL('smtp.gmail.com', 465) as smtp_server:
#        smtp_server.login(sender_email, password)
#        smtp_server.sendmail(sender_email, receiver_email, msg.as_string())
#        print("Message sent!")
 
 
 
def welcome_send_mail(receiver_email):
 
    # Connect to the SMTP server and send the email
    email_body = """
    <html>
    <title>Welcome to USF Rockys chatbot</title>
    <body>
        Hello👋,<br>
        <br>
        Welcome to University of South Florida (USF)!How can I assist you today?<br>
        <br>
        If you have any questions about the MS BAIS program, USF housing options, USF on-campus employment, or immigration questions. Please feel free to ask, and I'll do my best to provide you with the information you need.<br>
        <br>
        For further enquries you can reach out using the below information. When dropping the mail please include your U-Number! .<br>
        <br>
        <br>
        Thank you!
        <p>Contact information: Han Reichgelt<br>
        Graduate Coordinator, MS in Business Analytics & Information Systems<br>
        School of Information Systems and Management<br>
        Muma College of Business<br>
        Phone: (727) 873-4786<br>
        muma-msbais@usf.edu  </p>
    </body>
    </html>
    """
    # Create a MIMEText object with the HTML content
    message = MIMEMultipart("alternative")
    message["Subject"] = " Welcome to USF Rockys chatbot "
    message["From"] = sender_email
    message["To"] = receiver_email
    html_body = MIMEText(email_body, "html")
    message.attach(html_body)
    try:
        server = smtplib.SMTP_SSL(smtp_server, smtp_port)
       
        #server.login(sender_email, password)
        server.login(GMAIL_USERNAME, GMAIL_APP_PASSWORD)
        server.sendmail(sender_email, receiver_email, message.as_string())
        server.quit()
        print("Email sent successfully")
    except Exception as e:
        print(f"An error occurred: {str(e)}")
 
def end_send_mail(receiver_email):
 
    # Connect to the SMTP server and send the email
    email_body = """
    <html>
    <title>Welcome to Rockys Bot chat</title>
    <body>
        <p>
            Contact information: Han Reichgelt<br>
            Graduate Coordinator, MS in Business Analytics & Information Systems<br>
            School of Information Systems and Management<br>
            Muma College of Business<br>
            Phone: (727) 873-4786<br>
            muma-msbais@usf.edu</p>
    </body>
    </html>
    """
 
    # Create a MIMEText object with the HTML content
    message = MIMEMultipart("alternative")
    message["Subject"] = "Thank ypu for using USF mail id"
    message["From"] = sender_email
    message["To"] = receiver_email
    html_body = MIMEText(email_body, "html")
    message.attach(html_body)
 
    try:
        server = smtplib.SMTP_SSL(smtp_server, smtp_port)
        server.starttls()  # Use TLS (for Gmail)
        #server.login(sender_email, password)
        server.login(GMAIL_USERNAME, GMAIL_APP_PASSWORD)
        server.sendmail(sender_email, receiver_email, message.as_string())
        server.quit()
        print("Email sent successfully")
    except Exception as e:
        print(f"An error occurred: {str(e)}")
 
 
#welcome_send_mail("rmuralidharr22@gmail.com")