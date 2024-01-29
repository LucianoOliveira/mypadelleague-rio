from flask import Blueprint, render_template, request, flash, jsonify, redirect, url_for, Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import login_required, current_user
from .models import Players
from . import db
import json, os
from datetime import datetime, date, timedelta
from sqlalchemy import and_, func, cast, String


views =  Blueprint('views', __name__)

@views.route('/', methods=['GET', 'POST'])
def home():
    return render_template("index.html", user=current_user)




@views.route('/display_user_image/<userID>')
def display_user_image(userID):
    filePath = str(os.path.abspath(os.path.dirname(__file__)))+'/static/photos/users/'+str(userID)+'/main.jpg'
    if os.path.isfile(filePath):
        return redirect(url_for('static', filename='photos/users/'+ str(userID)+'/main.jpg'), code=301)
    else:
        return redirect(url_for('static', filename='photos/users/nophoto.jpg'), code=301)
    