import logging
import uuid
import threading

import violett.send_email

from flask import Blueprint, render_template, request, url_for, redirect

violett = Blueprint('violett', __name__, template_folder='templates',
                               static_folder='static', url_prefix='/archiv/violett')

def count_free():
    count1 = 40
    with open('data/violett/participant.csv', 'r') as file:
        for line in file.readlines():
           count1 -= 1 + int(line.split(";")[-1])
    return count1

@violett.route('/', methods=['GET', 'POST'])
def home():
    if request.method == 'POST':
        user_id = str(uuid.uuid4())
        email = request.form['email']
        firstname = request.form['firstname']
        lastname = request.form['lastname']
        companions = request.form['companions']
        
        count = count_free()
        if int(companions) + 1 > count:
            return render_template('violett.html',count_time1=count)
        
        with open('data/violett/participant.csv', 'a') as file:
            file.write(";".join([user_id,email,firstname,lastname,companions])+ "\n")
                 
        trd = threading.Thread(target=send_email.send_confirm_email, args=(email, user_id, firstname, companions,))
        trd.start()
        
        count = count_free()
        return render_template('violett.html', count_time1=count)
    count = count_free()
    return render_template('violett.html',count_time1=count)

@violett.route('/cancel/<id>')
def cancel(id):
    with open("data/violett/participant.csv", "r") as f:
        lines = f.readlines()
    with open("data/violett/participant.csv", "w") as f:
        for line in lines:
            if line.split(";")[0] != id:
                f.write(line)
    return redirect(url_for('violett.home'))
