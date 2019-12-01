import time
import multiprocessing

from Jumpscale import j

from .base import Base


class TestBCDB(Base):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.model = self.create_model()

    def create_model(self):
        scm = """
        @url = test.schema.1
        name** = "" (S)
        """
        schema = j.data.schema.get_from_text(scm)
        model = self.bcdb.model_get(schema=schema)
        return model

    def write(self, write_result):
        name = j.data.idgenerator.generateXCharID(1024 * 1024)

        write_start = time.time()
        obj = self.model.new()
        obj.name = name
        obj.save()
        write_end = time.time()

        write_time = write_end - write_start
        write_result.append(write_time)
