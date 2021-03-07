import logging

from flask import Blueprint, render_template, request, url_for

formular = Blueprint('formular', __name__, template_folder='templates',
                               static_folder='static', url_prefix='/formular')

@formular.route('/', methods=['GET', 'POST'])
def main():
    if request.method == 'POST':
        email = request.form['email']
        time = request.form['time']
        firstname = request.form['firstname']
        lastname = request.fornm['lastname']
        if time == 1:
            with open('data/time_one.csv', 'w') as file:
                file.write(";".join([email,firstname,lastname]))              
        else:
            with open('data/time_two.csv', 'w') as file:
                file.write(";".join([email,firstname,lastname])) 
        
        return render_template('formular.html')
        
    return render_template('formular.html')