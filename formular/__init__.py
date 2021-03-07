import logging
import uuid

import formular.send_email

from flask import Blueprint, render_template, request, url_for, redirect

formular = Blueprint('formular', __name__, template_folder='templates',
                               static_folder='static', url_prefix='/formular')

def count_free():
    count1 = 50
    count2 = 50
    with open('formular/data/participant.csv', 'r') as file:
        for line in file.readlines():
            if int(line.split(";")[-1]) == 1:
                count1 -= 1 + int(line.split(";")[-2])
            else:
                count2 -= 1 + int(line.split(";")[-2])
    return [count1, count2]

@formular.route('/', methods=['GET', 'POST'])
def home():
    if request.method == 'POST':
        user_id = str(uuid.uuid4())
        email = request.form['email']
        time = request.form['time']
        firstname = request.form['firstname']
        lastname = request.form['lastname']
        companions = request.form['companions']
        
        with open('formular/data/participant.csv', 'a') as file:
            file.write(";".join([user_id,email,firstname,lastname,companions, time])+ "\n")              
                
        send_email.send_confirm_email(email, user_id, firstname, time, companions)
        count = count_free()
        return render_template('formular.html', count_time1=count[0], count_time2=count[1])
    count = count_free()
    return render_template('formular.html',count_time1=count[0], count_time2=count[1])

@formular.route('/cancel/<id>')
def cancel(id):
    with open("formular/data/participant.csv", "r") as f:
        lines = f.readlines()
    with open("formular/data/participant.csv", "w") as f:
        for line in lines:
            if line.split(";")[0] != id:
                f.write(line)
    return redirect(url_for('formular.home'))
