import logging
import uuid

import meterstab.send_email

from flask import Blueprint, render_template, request, url_for, redirect

meterstab = Blueprint('meterstab', __name__, template_folder='templates',
                               static_folder='static', url_prefix='/meterstab')

def count_free():
    count1 = 50
    count2 = 50
    with open('meterstab/data/participant.csv', 'r') as file:
        for line in file.readlines():
            if int(line.split(";")[-1]) == 1:
                count1 -= 1 + int(line.split(";")[-2])
            else:
                count2 -= 1 + int(line.split(";")[-2])
    return [count1, count2]

@meterstab.route('/', methods=['GET', 'POST'])
def home():
    if request.method == 'POST':
        user_id = str(uuid.uuid4())
        email = request.form['email']
        time = request.form['time']
        firstname = request.form['firstname']
        lastname = request.form['lastname']
        companions = request.form['companions']
        
        with open('meterstab/data/participant.csv', 'a') as file:
            file.write(";".join([user_id,email,firstname,lastname,companions, time])+ "\n")              
                
        send_email.send_confirm_email(email, user_id, firstname, time, companions)
        count = count_free()
        return render_template('meterstab.html', count_time1=count[0], count_time2=count[1])
    count = count_free()
    return render_template('meterstab.html',count_time1=count[0], count_time2=count[1])

@meterstab.route('/cancel/<id>')
def cancel(id):
    with open("meterstab/data/participant.csv", "r") as f:
        lines = f.readlines()
    with open("meterstab/data/participant.csv", "w") as f:
        for line in lines:
            if line.split(";")[0] != id:
                f.write(line)
    return redirect(url_for('meterstab.home'))