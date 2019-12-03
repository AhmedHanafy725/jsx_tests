import os
import time
import multiprocessing

from Jumpscale import j


BLOCKSIZE = 1024 * 1024 * 5


class TestBCDB:
    def __init__(self, **kwargs):
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
            j.core.db
            storclient = j.clients.rdb.client_get(namespace="test_rdb")
            bcdb = j.data.bcdb.get(name="test", storclient=storclient, reset=False)
            return bcdb
        else:
            bcdb = j.data.bcdb.get("test")
            return bcdb

    def write_string(self, write_result):
        text = j.data.idgenerator.generateXCharID(BLOCKSIZE)
        string_model = self.string_model.new()
        string_model.text = text

        write_start = time.time()
        string_model.save()
        write_end = time.time()

        write_time = write_end - write_start
        write_result.append(write_time)

    def write_nested(self, write_result):
        text = j.data.idgenerator.generateXCharID(BLOCKSIZE)
        string_model = self.string_model.new()
        string_model.text = text
        string_model.save()
        nested_model = self.nested_model.new()
        nested_model.string_obj = string_model

        write_start = time.time()
        nested_model.save()
        write_end = time.time()

        write_time = write_end - write_start
        write_result.append(write_time)

    def write_indexed_string(self, write_result):
        text = j.data.idgenerator.generateXCharID(BLOCKSIZE)
        name = j.data.idgenerator.generateXCharID(15)
        indexed_model = self.indexed_model.new()
        indexed_model.text = text
        indexed_model.name = name

        write_start = time.time()
        indexed_model.save()
        write_end = time.time()

        write_time = write_end - write_start
        write_result.append(write_time)
