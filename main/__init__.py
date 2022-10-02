from flask import Flask, request, render_template, url_for, jsonify, redirect, abort, flash, session
from flask_wtf import CSRFProtect
from flask_pymongo import PyMongo
from bson.objectid import ObjectId
from datetime import datetime
import time
import math
from datetime import timedelta
import os

app = Flask(__name__)
csrf = CSRFProtect(app)
app.config["MONGO_URI"] =  "mongodb://localhost:27017/myweb"
mongo = PyMongo(app)    # mongo 가 myweb을 가르킴
app.config['SECRET_KEY'] = "gahoo11sdf1"
app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(minutes=30)

ALLOWED_EXTENSIONS = set(['txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif'])

# image upload 설정
BOARD_IMAGE_PATH = "C:\\coding\\01study\\inflean\\images"
app.config['BOARD_IMAGE_PATH'] = BOARD_IMAGE_PATH
if not os.path.exists(app.config['BOARD_IMAGE_PATH']):
    os.mkdir(app.config['BOARD_IMAGE_PATH'])  
    
app.config['MAX_CONTENT_LENGTH'] = 15 * 1024 * 1024

# file upload 설정
BOARD_ATTACH_FILE_PATH = "C:\\coding\\01study\\inflean\\upload"
app.config['BOARD_ATTACH_FILE_PATH'] = BOARD_ATTACH_FILE_PATH
if not os.path.exists(app.config['BOARD_ATTACH_FILE_PATH']):
    os.mkdir(app.config['BOARD_ATTACH_FILE_PATH'])


from .common import login_required, allowed_file, rand_generate, check_filename, hash_password, check_password
from .filter import format_datetime
from . import board
from . import member
from . import main

app.register_blueprint(board.bp)
app.register_blueprint(member.bp)
app.register_blueprint(main.bp)
