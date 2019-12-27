from flask import Flask

appvar = Flask(__name__)

from app import routes

