import logging
import os
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

log = logging.getLogger('smtphelp')

def send(conf, subject, body):
  if conf['smtp'].get('secure'):
    server = smtplib.SMTP_SSL(timeout=conf['smtp']['timeoutSeconds'])  
  else:
    server = smtplib.SMTP(timeout=conf['smtp']['timeoutSeconds'])  

  if conf['smtp'].get('debug'):
    log.info("Enabled debug logging")
    server.set_debuglevel(True)

  log.info("Connecting to server; host=%s; port=%d" % (conf['smtp']['host'], conf['smtp']['port']))
  server.connect(host=conf['smtp']['host'], 
                 port=conf['smtp']['port'])

  server.ehlo()
  if conf['smtp'].get('starttls'):
    log.info("Enabled TLS secure mode")
    server.starttls()
    server.ehlo()

  username = os.environ.get('SMTP_USERNAME')
  password = os.environ.get('SMTP_PASSWORD')
  if username and password:
    log.info("Sending username and password")
    server.login(username, password)

  if conf['smtp'].get('subjectPrefix'):
    subject = conf['smtp'].get('subjectPrefix') + subject
    
  msg = MIMEMultipart()
  msg['From'] = conf['smtp']['from']
  msg['To'] = conf['smtp']['to']
  msg['Subject'] = subject
  msg.attach(MIMEText(str(body)))
  message = msg.as_string()

  log.info("Sending email; length=%d" % (len(message)))
  server.sendmail(conf['smtp']['from'], conf['smtp']['to'], message)
  server.quit()
