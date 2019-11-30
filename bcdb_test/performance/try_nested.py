from Jumpscale import j
import time
import multiprocessing


class DB:
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

    @staticmethod
    def create_obj_model():
        scm = """
        @url = test.obj.1
        obj = (O) !test.schema.1
        """
        schema = j.data.schema.get_from_text(scm)
        bcdb = j.data.bcdb.get("test")
        model = bcdb.model_get(schema=schema)
        return model


class TestBCDB:

    def write(self, obj_model, text_model, write_result):
        name = j.data.idgenerator.generateXCharID(1024 * 1024)

        write_start = time.time()
        text = text_model.new()
        text.name = name
        obj = obj_model.new()
        obj.obj = text
        obj.save()
        write_end = time.time()

        write_time = write_end - write_start
        write_result.append(write_time)

    def process(self, process_number, text_model, obj_model):
        manager = multiprocessing.Manager()
        write_result = manager.list()
        jobs = []
        for i in range(process_number):
            process = multiprocessing.Process(target=self.write, args=(text_model, obj_model, write_result,))
            jobs.append(process)
            process.start()

        for proc in jobs:
            proc.join()

        return write_result

if __name__ == "__main__":
    test = TestBCDB()
    text_model = DB.create_model()
    obj_model = DB.create_obj_model()
    for i in range(1, 30, 5):
        write_result = test.process(process_number=i, text_model=text_model, obj_model=obj_model)

        print(f"For {i} processes: ", " write speed: {} MB/s".format(len(write_result) / sum(write_result)))

    # r_start = time.time()
    # read = model.find()
    # r_stop = time.time()

    # r_time = r_stop - r_start

    # print("read speed:", len(read) / r_time, "MB/s")
