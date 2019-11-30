from mongoengine import fields, Document, connect
import time
from Jumpscale import j
import multiprocessing


class OBJ(Document):
    name = fields.StringField(required=True)
    meta = {"collection": "test"}


class MongoDB:
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.db_connect()

    def db_connect(self):
        connect(db="test", connect=False)


class TestMonog:
    def write(self, write_result):
        name = j.data.idgenerator.generateXCharID(1024 * 1024)

        write_start = time.time()
        obj = OBJ()
        obj.name = name
        obj.save()
        write_end = time.time()

        write_time = write_end - write_start
        write_result.append(write_time)

    def process(self, process_number):
        manager = multiprocessing.Manager()
        write_result = manager.list()
        jobs = []
        for i in range(process_number):
            process = multiprocessing.Process(target=self.write, args=(write_result,))
            jobs.append(process)
            process.start()

        for proc in jobs:
            proc.join()

        return write_result
