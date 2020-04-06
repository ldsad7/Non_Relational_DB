from flask import Flask

from app.db import RedisDatabase
from config import Config

app = Flask(__name__)
app.config.from_object(Config)

redis = RedisDatabase()

from app import routes
