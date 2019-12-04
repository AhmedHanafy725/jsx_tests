import time

from Jumpscale import j
import matplotlib.pyplot as plt

from .base_test import BaseTest
from .framework.bcdb import TestBCDB
from .framework.mongodb import TestMongo
from .framework.mongo_models.models import *
from .framework.redis import Redis


class PerformanceTest(BaseTest):
    def setUp(self):
        super().setUp()
        self.bcdb = TestBCDB(type="redis")
        self.bcdb.create_models()
        self.mongo = TestMongo()
        self.mongo.create_models()

    def tearDown(self):
        self.bcdb.bcdb.reset()
        self.mongo.mongodb.drop_database("test")
        self.mongo.disconnect()
        super().tearDown()

    def write_two_field_string(self, block_size=1024, key=None, value=None):
        if (key is None) and (value is None):
            name = j.data.idgenerator.generateXCharID(15)
            text = j.data.idgenerator.generateXCharID(block_size)
        elif (key is not None) and (value is None):
            name = key
            text = j.data.idgenerator.generateXCharID(block_size)
        elif (key is None) and (value is not None):
            name = j.data.idgenerator.generateXCharID(15)
            text = value
        else:
            name = key
            text = value

        mongo_model = StrIndexedDoc()
        mongo_model.text = text
        mongo_model.name = name
        mongo_model.save()

        bcdb_model = self.bcdb.indexed_model.new()
        bcdb_model.text = text
        bcdb_model.name = name
        bcdb_model.save()

    def calculate_write_speed(self, processes, func):
        speed = []
        for i in processes:
            write_result = self.multi_process(target=func, process_number=i)
            self.assertGreaterEqual(len(write_result), 0.9 * i, "The objects that should be saved are less than 90%")
            speed.append(len(write_result) / sum(write_result))
        return speed

    def query_speed(self, query_func, name, value):
        time_start = time.time()
        target = query_func(name=name)
        time_stop = time.time()

        time_taken = time_stop - time_start
        self.assertTrue(target)
        self.assertEqual(target[0].text, value)
        return time_taken

    def test001_write_5_mb_string(self):
        """
        Test case for writing 5 MB of string in parallel in BCDB, MongoDB and Redis using mutli processes.
        
        **Test scenario**
        #. Write in BCDB.
        #. Write in MongoDB.
        #. Write in Redis.
        #. Generate chart for writing speed for the three DataBases.
        """
        processes = [1, 5, 10, 25, 50]

        self.info("Writing in BCDB.")
        bcdb_speed = self.calculate_write_speed(processes=processes, func=self.bcdb.write_string)

        self.info("Writing in MongoDB.")
        mongo_speed = self.calculate_write_speed(processes=processes, func=self.mongo.write_string)

        self.info("Writing in Redis.")
        redis = Redis()
        redis_speed = self.calculate_write_speed(processes=processes, func=redis.write_string)

        self.info("Generating chart for writing speed for the three DataBases.")
        plt.title = "Writing 5 MB of string on DataBase in parallel using multi processes (Higher speed is better)"
        plt.yaxis = "Speed in MB/s"
        plt.xaxis = "Number of processes"
        plt.plot(processes, bcdb_speed, label="BCDB(redis)")
        plt.plot(processes, mongo_speed, label="MongoBD")
        plt.plot(processes, redis_speed, label="Redis")
        plt.legend()
        plt.savefig("write_speed.png")

    def test002_write_5_mb_string_nested_schema(self):
        """
        Test case for writing 5 MB of string in nested schema in parallel using mutli processes in BCDB and MongoDB.
        
        **Test scenario**
        #. Write in BCDB.
        #. Write in MongoDB.
        #. Generate chart for writing speed for the both DataBases.
        """
        processes = [1, 5, 10, 25, 50]

        self.info("Write in BCDB.")
        bcdb_speed = self.calculate_write_speed(processes=processes, func=self.bcdb.write_nested)

        self.info("Write in MongoDB.")
        mongo_speed = self.calculate_write_speed(processes=processes, func=self.mongo.write_nested)

        self.info("Generate chart for writing speed for the both DataBases.")
        plt.title = "Writing 5 MB of string in nested schema on DataBase in parallel using multi processes (Higher speed is better)"
        plt.yaxis = "Speed in MB/s"
        plt.xaxis = "Number of processes"
        plt.plot(processes, bcdb_speed, label="BCDB(redis)")
        plt.plot(processes, mongo_speed, label="MongoBD")
        plt.legend()
        plt.savefig("nested_write_speed.png")

    def test003_write_15_char_indexed_string(self):
        """
        Test case for writing 5 MB of string with 15 indexed character in parallel using mutli processes in BCDB, MongoDB and Redis.
        
        **Test scenario**
        #. Write in BCDB.
        #. Write in MongoDB.
        #. Generate chart for writing speed for the both DataBases.
        """
        processes = [1, 5, 10, 25, 50]

        self.info("Write in BCDB.")
        bcdb_speed = self.calculate_write_speed(processes=processes, func=self.bcdb.write_indexed_string)

        self.info("Write in MongoDB.")
        mongo_speed = self.calculate_write_speed(processes=processes, func=self.mongo.write_indexed_string)

        self.info("Generate chart for writing speed for the both DataBases.")
        plt.title = "Writing 5 MB of string with 15 indexed character on DataBase in parallel using multi processes (Higher speed is better)"
        plt.yaxis = "Speed in MB/s"
        plt.xaxis = "Number of processes"
        plt.plot(processes, bcdb_speed, label="BCDB(redis)")
        plt.plot(processes, mongo_speed, label="MongoBD")
        plt.legend()
        plt.savefig("indexed_write_speed.png")

    def test004_query(self):
        """
        Test case for querying in DataBase with changing the number of objects.
        
        **Test scenario**
        #. Write random data in BCDB and mongoDB and set specific value (V1) in the middle of this data.
        #. Query BCDB for (V1) and calculate the time that has been taken.
        #. Query MongoDB for (V1) and calculate the time that has been taken.
        #. Generate chart for querying time for the both DataBases.
        """
        data_sizes = [100, 100, 300, 500, 9000]
        bcdb_query_time = []
        mongo_query_time = []
        self.info(f"Write random data in BCDB and mongoDB and set specific value (V1) in the middle of this data")
        for data_size in data_sizes:
            for i in range(data_size):
                if i == data_size / 2:
                    name = j.data.idgenerator.generateXCharID(15)
                    text = j.data.idgenerator.generateXCharID(1024)
                    self.write_two_field_string(key=name, value=text)
                    continue
                self.write_two_field_string()

            self.info("Query BCDB for (V1) and calculate the time that has been taken.")
            query_func = self.bcdb.indexed_model.find
            query_time = self.query_speed(query_func, name, text)
            bcdb_query_time.append(query_time)

            self.info("Query MongoDB for (V1) and calculate the time that has been taken.")
            query_func = StrIndexedDoc.objects
            query_time = self.query_speed(query_func, name, text)
            mongo_query_time.append(query_time)

        self.info("Generate chart for querying time for the both DataBases")
        bcdb_query_time = [x * 1000 for x in bcdb_query_time]
        mongo_query_time = [x * 1000 for x in mongo_query_time]
        data_sizes = [100, 200, 500, 1000, 10000]
        plt.title = (
            "Querying in DataBase with 15 indexed character with changing number of objects (Lower time is better)"
        )
        plt.yaxis = "Time in ms"
        plt.xaxis = "Number of objects stored"
        plt.plot(data_sizes, bcdb_query_time, label="BCDB(redis)")
        plt.plot(data_sizes, mongo_query_time, label="MongoBD")
        plt.legend()
        plt.savefig("query.png")
