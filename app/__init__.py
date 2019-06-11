from flask import Flask

app = Flask(__name__)
# app.config.from_object('config')
app.static_folder = 'static'

from app import views
