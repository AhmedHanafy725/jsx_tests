import time
import multiprocessing

from mongoengine import fields, Document, connect, disconnect_all
from Jumpscale import j

from .mongo_models.models import *
from .base import Base

BLOCKSIZE = 1024 * 1024 * 5


class TestMongo(Base):
    def __init__(self, **kwargs):
        super().__init__()
        self.mongodb = self.db_connect()

    def create_models(self):
        self.string_model = StrDoc
        self.nested_model = Nested
        self.str_indexed_model = StrIndexedDoc
        string_doc = self.string_model().save()
        nested_doc = self.nested_model(string_obj=string_doc).save()
        str_indexed_doc = self.str_indexed_model().save()

    def db_connect(self):
        return connect(db="test", connect=False)

    def disconnect(self):
        disconnect_all()

    def create_obj(self, model):
        return model()
