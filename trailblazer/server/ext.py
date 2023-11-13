from flask import Flask
from trailblazer.store.database import initialize_database
from trailblazer.store.store import Store


class FlaskStore(Store):
    def __init__(self, app=None):
        if app:
            self.init_app(app)

    def init_app(self, app: Flask):
        uri = app.config["SQLALCHEMY_DATABASE_URI"]
        initialize_database(uri)
        super(FlaskStore, self).__init__()


store = FlaskStore()
