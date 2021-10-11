import smtplib
import socket
import getpass
from datetime import datetime, date, time
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

# Prerequisites:
# - postfix server installed and configured to send mails.
# To test it, logon to the host and send an e-mail with: mail -s "Testmail" markus.bartels@guest.hpi.de <<< 'Testmail'
def send_test_mail():
    '''
    Message to test the Python e-mailing options.
    '''
    now = datetime.now()
    timestamp = now.strftime("%d.%m.%Y %H:%M:%S")

    hostname = socket.gethostname()
    username = getpass.getuser()
    sender_mail_address = username + "@" + hostname
    receiver_mail_address = "markus.bartels@guest.hpi.de"

    msg = MIMEMultipart()
    msg['From'] = sender_mail_address
    msg['To'] = receiver_mail_address
    msg['Subject'] = "Testmail"
    email_text = "Testmail: %s" % timestamp
    msg.attach(MIMEText(email_text, 'plain'))

    server = smtplib.SMTP('localhost', '25')
    server.send_message(msg)
    server.quit()

def send_error_mail_to_multiple_receivers(receiver_mail_addresses, error_message, logfilename):
    for receiver_mail_address in receiver_mail_addresses:
        send_error_mail(receiver_mail_address, error_message + "\nLogfile: " + logfilename)

def send_error_mail(receiver_mail_address, error_message):
    '''
    Sends the exception or error message to the configured receivers.
    '''
    hostname = socket.gethostname()
    username = getpass.getuser()
    sender_mail_address = username + "@" + hostname

    msg = MIMEMultipart()
    msg['From'] = sender_mail_address
    msg['To'] = receiver_mail_address
    msg['Subject'] = "An S3 backup error has occured"
    msg.attach(MIMEText(str(error_message), 'plain'))

    server = smtplib.SMTP('localhost', '25')
    server.send_message(msg)
    server.quit()
