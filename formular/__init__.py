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
        
        
    return render_template('formular.html')