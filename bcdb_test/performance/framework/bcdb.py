import os
import time
import multiprocessing

from Jumpscale import j

from .base import Base


class TestBCDB(Base):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        type = kwargs.get("type")
        self.bcdb = self.create_bcdb(type=type)

    def get_model(self, url):
        return self.bcdb.model_get(url=url)

    def create_models(self):
        models_path = os.path.join(os.path.dirname(__file__), "bcdb_models")
        self.bcdb.models_add(path=models_path)
        self.string_model = self.get_model(url="test.schema.1")
        self.nested_model = self.get_model(url="test.nested.1")
        self.indexed_model = self.get_model(url="test.index.1")

    def create_bcdb(self, type):
        if type == "redis":
            storclient = j.clients.rdb.client_get(namespace="test_rdb")
            bcdb = j.data.bcdb.get(name="test", storclient=storclient, reset=False)
            return bcdb
        else:
            bcdb = j.data.bcdb.get("test")
            return bcdb

    def create_obj(self, model):
        return model.new()
