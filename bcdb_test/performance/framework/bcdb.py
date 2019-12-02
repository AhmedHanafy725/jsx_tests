import time
import multiprocessing

from Jumpscale import j

from .base import Base


class TestBCDB(Base):
    def __init__(self, **kwargs):
        type = kwargs.get("type")
        self.bcdb = self.create_bcdb(type=type)
        self.string_model = self.create_string_model()
        self.nested_model = self.create_nested_model()
        self.indexed_model = self.create_indexed_string_model()
        self.two_field_model = self.create_two_field_string_model()

    def create_bcdb(self, type):
        if type == "redis":
            j.core.db
            storclient = j.clients.rdb.client_get(namespace="test_rdb")
            bcdb = j.data.bcdb.get(name="test", storclient=storclient, reset=False)
            return bcdb
        else:
            bcdb = j.data.bcdb.get("test")
            return bcdb

    def create_string_model(self):
        scm = """
        @url = test.schema.1
        text = "" (S)
        """
        schema = j.data.schema.get_from_text(scm)
        model = self.bcdb.model_get(schema=schema)
        return model
    
    def create_nested_model(self):
        scm = """
        @url = test.nested.1
        string_obj = (O) !test.schema.1
        """
        schema = j.data.schema.get_from_text(scm)
        model = self.bcdb.model_get(schema=schema)
        return model

    def create_indexed_string_model(self):
        scm = """
        @url = test.index.1
        name** = (S)
        text = "" (S)
        """
        schema = j.data.schema.get_from_text(scm)
        model = self.bcdb.model_get(schema=schema)
        return model

    def create_two_field_string_model(self):
        scm = """
        @url = test.two.field.1
        name = (S)
        text = "" (S)
        """
        schema = j.data.schema.get_from_text(scm)
        model = self.bcdb.model_get(schema=schema)
        return model


    def write_string(self, write_result):
        text = j.data.idgenerator.generateXCharID(1024 * 1024 * 5)
        string_model = self.string_model.new()
        string_model.text = text

        write_start = time.time()
        string_model.save()
        write_end = time.time()

        write_time = write_end - write_start
        write_result.append(write_time)

    def write_nested(self, write_result):
        text = j.data.idgenerator.generateXCharID(1024 * 1024 * 5)
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
        text = j.data.idgenerator.generateXCharID(1024 * 1024 * 5)
        name = j.data.idgenerator.generateXCharID(15)
        indexed_model = self.indexed_model.new()
        indexed_model.text = text
        indexed_model.name = name

        write_start = time.time()
        indexed_model.save()
        write_end = time.time()

        write_time = write_end - write_start
        write_result.append(write_time)

    def write_two_field_string(self, index=False, key=None, value=None):
        if (key is None) and (value is None):
            name = j.data.idgenerator.generateXCharID(15)
            text = j.data.idgenerator.generateXCharID(1024)
        elif (key is not None) and (value is None):
            name = key
            text = j.data.idgenerator.generateXCharID(1024)
        elif (key is None) and (value is not None):
            name = j.data.idgenerator.generateXCharID(15)
            text = value
        else:
            name = key
            text = value
        
        if index:
            two_field_model = self.indexed_model.new()
        else:
            two_field_model = self.two_field_model.new()
        two_field_model.text = text
        two_field_model.name = name
        two_field_model.save()
        