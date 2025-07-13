#!/usr/bin/python
import smtplib,ssl
import argparse
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email.mime.text import MIMEText
from email.utils import formatdate
from email import encoders
import sys

username = 'USERNAME'
password = 'PASSWORD'
server="EMAIL_SERVER"
port=587


parser = argparse.ArgumentParser(description='Send mail.')
parser.add_argument('--to', nargs='?', help='recipient')
parser.add_argument('--subject', nargs='?', help='subject')
args = parser.parse_args()

def send_mail(send_to,subject,text,isTls=True):
    msg = MIMEMultipart()
    msg['From'] = username
    msg['To'] = send_to
    msg['Date'] = formatdate(localtime = True)
    msg['Subject'] = subject
    msg.attach(MIMEText(text))

    smtp = smtplib.SMTP(server, port)
    if isTls:
        smtp.starttls()
    smtp.login(username,password)
    failed_addresses = smtp.sendmail(msg['From'], msg['To'].split(","), msg.as_string())
    print(failed_addresses)
    smtp.quit()

send_mail(args.to, args.subject, sys.stdin.read())


