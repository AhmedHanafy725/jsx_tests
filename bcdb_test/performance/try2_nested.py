from mongoengine import fields, Document, connect
import time
from Jumpscale import j
import multiprocessing


class Text(Document):
    name = fields.StringField(required=True)
    meta = {"collection": "name"}

class Obj(Document):
    obj = fields.ReferenceField(Text)
    meta = {"collection": "obj"}


class DB:
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.db_connect()

    def db_connect(self):
        connect(db="test", connect=False)


class TestMonog:
    def write(self, write_result):
        name = j.data.idgenerator.generateXCharID(1024 * 1024)

        write_start = time.time()
        text = Text()
        text.name = name
        text.save()
        obj = Obj()
        obj.obj = text
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

if __name__ == "__main__":
    db = DB()
    test = TestMonog()

    for i in range(1, 30, 5):
        write_result = test.process(process_number=i)

        print(f"For {i} processes: ", " write speed: {} MB/s".format(len(write_result) / sum(write_result)))

    # r_start = time.time()
    # read = OBJ.objects()
    # r_stop = time.time()

    # r_time = r_stop - r_start

    # print("read speed:", len(read) / r_time, "MB/s")
