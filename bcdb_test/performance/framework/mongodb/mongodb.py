import time
import multiprocessing

from mongoengine import fields, Document
from Jumpscale import j

from .base import Base


class OBJ(Document):
    name = fields.StringField(required=True)
    meta = {"collection": "test"}


class TestMongo(Base):
    def write(self, write_result):
        name = j.data.idgenerator.generateXCharID(1024 * 1024)

        write_start = time.time()
        obj = OBJ()
        obj.name = name
        obj.save()
        write_end = time.time()

        write_time = write_end - write_start
        write_result.append(write_time)
