from flask import Flask, request, render_template, url_for, jsonify, redirect, abort, flash, session
from flask_pymongo import PyMongo
from bson.objectid import ObjectId
from datetime import datetime
import time
import math
from datetime import timedelta



app = Flask(__name__)
app.config["MONGO_URI"] =  "mongodb://localhost:27017/myweb"
mongo = PyMongo(app)    # mongo 가 myweb을 가르킴
app.config['SECRET_KEY'] = "gahoo11sdf1"
app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(minutes=30)

from .common import login_required
from .filter import format_datetime
from . import board
from . import member

app.register_blueprint(board.bp)
app.register_blueprint(member.bp)
