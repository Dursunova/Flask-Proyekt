from flask import Flask
from flask_wtf.csrf import CSRFProtect

app= Flask(__name__)

app.config["SQLALCHEMY_DATABASE_URI"]="mysql://root:12345@localhost:3308/products_db"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = True
# app.config['SECRET_KEY'] = 'my-secret-pw' 

from controllers import *
from extensions import *
from models import *
from forms import *

csrf = CSRFProtect(app)


if __name__ == '__main__':
    app.run(debug=True,host ='localhost',port = 5000)