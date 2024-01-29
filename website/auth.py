from flask import Blueprint, render_template, request, flash, redirect, url_for
from .models import Players
from werkzeug.security import generate_password_hash, check_password_hash
# from . import db, emailS
from . import db
from flask_login import login_user, login_required, logout_user, current_user
import os
# from flask_mail import Mail, Message
# from itsdangerous import URLSafeTimedSerializer, SignatureExpired


auth =  Blueprint('auth', __name__)
# s = URLSafeTimedSerializer('Thisisasecret123!')