from flask import Blueprint, render_template, request, flash, redirect
from flask_login import login_required,current_user


auth = Blueprint('auth',__name__,template_folder='auth_templates')