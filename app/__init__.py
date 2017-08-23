from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime


class SRPAException(Exception):
    def __init__(self, message, description):
        super(SRPAException, self).__init__(message)
        self.message = message
        self.description = description
        self.timestamp = datetime.now()
        print(self.message, self.description, self.timestamp)


class FileNotSupportedException(SRPAException):
    def __init__(self):
        super(FileNotSupportedException, self).__init__(
            message='Formato no soportado', description='Solo son soportados los archivos csv y xlsx')

app = Flask(__name__)
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)
