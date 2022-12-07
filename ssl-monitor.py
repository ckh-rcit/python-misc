import datetime
import ssl
import smtplib

# Set the number of days before expiration to send the email
THRESHOLD_DAYS = 30

# Set the email address to send the notification to
NOTIFICATION_EMAIL = "example@example.com"

# Set the SMTP server and port to use for sending the email
SMTP_SERVER = "smtp.example.com"
SMTP_PORT = 465

# Set the SMTP username and password
SMTP_USERNAME = "username"
SMTP_PASSWORD = "password"

# Set the SSL certificates to monitor
CERTIFICATES = [
    "example.com",
    "www.example.com",
    "example.org",
    "www.example.org",
]

# This function checks the expiration date of an SSL certificate
def check_certificate_expiration(hostname):
    ssl_date_fmt = r"%b %d %H:%M:%S %Y %Z"

    context = ssl.create_default_context()
    conn = context.wrap_socket(
        socket.socket(socket.AF_INET),
        server_hostname=hostname,
    )
    # Set a short timeout to avoid hanging on slow connections
    conn.settimeout(3.0)

    try:
        conn.connect((hostname, 443))
        ssl_info = conn.getpeercert()
        # Get the notAfter date from the certificate
        expiration_date = datetime.datetime.strptime(
            ssl_info["notAfter"],
            ssl_date_fmt
        )
        # Return the number of days until expiration
        return (expiration_date - datetime.datetime.utcnow()).days
    except:
        return None

# This function sends an email using the specified SMTP server
def send_email(subject, body):
    msg = MIMEText(body)
    msg["Subject"] = subject
    msg["To"] = NOTIFICATION_EMAIL
    msg["From"] = SMTP_USERNAME

    with smtplib.SMTP_SSL(SMTP_SERVER, SMTP_PORT) as server:
        server.login(SMTP_USERNAME, SMTP_PASSWORD)
        server.send_message(msg)

# Check the expiration date of each certificate
for hostname in CERTIFICATES:
    days_until_expiration = check_certificate_expiration(hostname)
    if days_until_expiration is not None and days_until_expiration <= THRESHOLD_DAYS:
        # The certificate is about to expire, so send an email
        subject = f"SSL Certificate for {hostname} is expiring soon"
        body = f"The SSL certificate for {hostname} will expire in {days_until_expiration} days."
        send_email(subject, body)
