import logging
import uuid

import send_email

from flask import Blueprint, render_template, request, url_for, redirect

formular = Blueprint('formular', __name__, template_folder='templates',
                               static_folder='static', url_prefix='/formular')



@formular.route('/', methods=['GET', 'POST'])
def home():
    if request.method == 'POST':
        user_id = uuid.uuid4()
        email = request.form['email']
        time = request.form['time']
        firstname = request.form['firstname']
        lastname = request.form['lastname']
        companions = request.form['companions']
        if time == 1:
            with open('formular/data/time_one.csv', 'w') as file:
                file.write(";".join([user_id,email,firstname,lastname,companions]))              
        else:
            with open('formular/data/time_two.csv', 'w') as file:
                file.write(";".join([user_id, email,firstname,lastname, companions]))
        return render_template('formular.html')
    return render_template('formular.html')
