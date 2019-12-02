import time
import multiprocessing

from mongoengine import fields, Document, connect
from Jumpscale import j

from .base import Base


class StrDoc(Document):
    text = fields.StringField(required=True)
    meta = {"collection": "test.schema.1"}

class Nested(Document):
    string_obj = fields.ReferenceField(StrDoc)
    meta = {"collection": "test.nested.1"}

class StrIndexedDoc(Document):
    name = fields.StringField(required=True)
    text = fields.StringField(required=True)
    meta = {"collection": "test.index.1", "indexes": ["name"]}

class TwoFieldString(Document):
    name = fields.StringField(required=True)
    text = fields.StringField(required=True)
    meta = {"collection": "test.two.field.1"}

class TestMongo:
    def __init__(self, **kwargs):
        self.db_connect()

    def db_connect(self):
        connect(db="test", connect=False)

    def write_string(self, write_result):
        text = j.data.idgenerator.generateXCharID(1024 * 1024 * 5)
        string_doc = StrDoc()
        string_doc.text = text

        write_start = time.time()
        string_doc.save()
        write_end = time.time()

        write_time = write_end - write_start
        write_result.append(write_time)

    def write_nested(self, write_result):
        text = j.data.idgenerator.generateXCharID(1024 * 1024 * 5)
        string_doc = StrDoc()
        string_doc.text = text
        string_doc.save()
        nested_doc = Nested()
        nested_doc.string_obj = string_doc

        write_start = time.time()
        nested_doc.save()
        write_end = time.time()

        write_time = write_end - write_start
        write_result.append(write_time)

    def write_indexed_string(self, write_result):
        text = j.data.idgenerator.generateXCharID(1024 * 1024 * 5)
        name = j.data.idgenerator.generateXCharID(15)
        str_indexed_doc = StrIndexedDoc()
        str_indexed_doc.text = text
        str_indexed_doc.name = name

        write_start = time.time()
        str_indexed_doc.save()
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
            two_field_model = StrIndexedDoc()
        else:
            two_field_model = TwoFieldString()
        two_field_model.text = text
        two_field_model.name = name
        two_field_model.save()
        