from datetime import datetime

from . import db


class User(db.Document):
    email = db.EmailField(required=True, unique=True)
    password = db.StringField(required=True)
    token = db.StringField(required=True)


class Release(db.EmbeddedDocument):
    name = db.StringField()


class Module(db.EmbeddedDocument):
    name = db.StringField()


class Project(db.Document):
    name = db.StringField(required=True, unique=True)
    modules = db.EmbeddedDocumentListField(Module)
    releases = db.EmbeddedDocumentListField(Release)


class Step(db.EmbeddedDocument):
    description = db.StringField()
    status = db.StringField()
    screenshot = db.StringField()


class Test(db.Document):
    number = db.IntField()
    module = db.StringField()
    description = db.StringField()
    status = db.StringField()
    rerun = db.BooleanField()
    date = db.DateTimeField(default=datetime.utcnow)
    tags = db.ListField(db.StringField())
    steps = db.EmbeddedDocumentListField(Step)
