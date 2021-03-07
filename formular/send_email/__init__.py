import const

import smtplib, ssl
from email.mime.text import MIMEText

port = 465
password = const.baseshuttle_email_psw

context = ssl.create_default_context()



def send_confirm_email(to, user_id, name, time, companions):
    
    msg = ""
    with open('formular/send_email/template.html', 'r', encoding='utf-8') as f:
        msg = f.read()
    msg = msg.replace('$name', name)
    if int(time) == 1:
        msg = msg.replace('$time', '19.00 Uhr')
    else:
        msg = msg.replace('$time', '20.00 Uhr')
    msg = msg.replace('$companions', companions)
    msg = msg.replace('$url', "baseshuttle.de/formular/cancel/" + user_id)
    
    msg = MIMEText(msg, 'html')
    with smtplib.SMTP_SSL("smtp.strato.de", port=port, context=context) as server:
        server.login("info@baseshuttle.de", password)
        server.sendmail( "info@baseshuttle.de", to, msg.as_string())
        