from Jumpscale import j
import time
import multiprocessing


class BCDB:
    @staticmethod
    def create_model():
        scm = """
        @url = test.schema.1
        name** = "" (S)
        """
        schema = j.data.schema.get_from_text(scm)
        bcdb = j.data.bcdb.get("test")
        model = bcdb.model_get(schema=schema)
        return model


class TestBCDB:

    def write(self, model, write_result):
        name = j.data.idgenerator.generateXCharID(1024 * 1024)

        write_start = time.time()
        obj = model.new()
        obj.name = name
        obj.save()
        write_end = time.time()

        write_time = write_end - write_start
        write_result.append(write_time)

    def process(self, process_number, model):
        manager = multiprocessing.Manager()
        write_result = manager.list()
        jobs = []
        for i in range(process_number):
            process = multiprocessing.Process(target=self.write, args=(model, write_result,))
            jobs.append(process)
            process.start()

        for proc in jobs:
            proc.join()

        return write_result