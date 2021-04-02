import data.const as const


import smtplib, ssl
from email.mime.text import MIMEText

port = 465
password = const.baseshuttle_email_psw

context = ssl.create_default_context()



def send_confirm_email(to, user_id, name, time, companions):
    
    msg = ""
    with open('meterstab/send_email/email_template.html', 'r', encoding='utf-8') as f:
        msg = f.read()
    msg = msg.replace('$name', name)
    if int(time) == 1:
        msg = msg.replace('$time', ' Dienstag 30.3. 17:30 – 19:30 Uhr')
    else:
        msg = msg.replace('$time', 'Freitag 02.04. 10:00 – 12:00 Uhr')
    msg = msg.replace('$companions', str(int(companions)+1))
    msg = msg.replace('$url', "https://baseshuttle.de/meterstab/cancel/" + user_id)
    
    msg = MIMEText(msg, 'html')
    msg["Subject"] = 'Bestätigungsemail zu Meeterstab-Aktion-Anmeldung'
    
    
    server = smtplib.SMTP_SSL("smtp.strato.de", port)
    server.login("info@baseshuttle.de", password)
    server.sendmail("info@baseshuttle.de", to, msg.as_string())
    server.close()
        