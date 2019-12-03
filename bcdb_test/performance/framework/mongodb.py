import time
import multiprocessing

from mongoengine import fields, Document, connect, disconnect_all
from Jumpscale import j

from .mongo_models.models import *

BLOCKSIZE = 1024 * 1024 * 5


class TestMongo:
    def __init__(self, **kwargs):
        self.mongodb = self.db_connect()

    def create_models(self):
        string_doc = StrDoc().save()
        nested_doc = Nested(string_obj=string_doc).save()
        str_indexed_doc = StrIndexedDoc().save()

    def db_connect(self):
        return connect(db="test", connect=False)

    def disconnect(self):
        disconnect_all()

    def write_string(self, write_result):
        text = j.data.idgenerator.generateXCharID(BLOCKSIZE)
        string_doc = StrDoc()
        string_doc.text = text

        write_start = time.time()
        string_doc.save()
        write_end = time.time()

        write_time = write_end - write_start
        write_result.append(write_time)

    def write_nested(self, write_result):
        text = j.data.idgenerator.generateXCharID(BLOCKSIZE)
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
        text = j.data.idgenerator.generateXCharID(BLOCKSIZE)
        name = j.data.idgenerator.generateXCharID(15)
        str_indexed_doc = StrIndexedDoc()
        str_indexed_doc.text = text
        str_indexed_doc.name = name

        write_start = time.time()
        str_indexed_doc.save()
        write_end = time.time()

        write_time = write_end - write_start
        write_result.append(write_time)
