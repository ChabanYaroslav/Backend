from flask import Flask
from flask_restful import Resource, Api, reqparse

app = Flask("sps_backend")
api = Api(app)
