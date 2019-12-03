import time

from Jumpscale import j

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

    def test001_write_5_mb_string(self):
        """
        Test case for writing 5 MB of string in parallel using mutli processes in BCDB, MongoDB and Redis.
        
        **Test scenario**
        #. Writing in BCDB.
        #. Writing in MongoDB.
        #. Writing in Redis.
        #. Generating chart for writing speed for the three DataBases.
        """
        processes = [1, 5, 10, 25, 50]
        title = "Writing 5 MB of string on DataBase in parallel using multi processes (Higher speed is better)"
        yaxis = "Speed in MB/s"
        xaxis = "Number of processes"
        output_file = "write_speed.html"

        self.info("Writing in BCDB.")
        speed1 = []
        for i in processes:
            write_result = self.multi_process(target=self.bcdb.write_string, process_number=i)
            self.assertGreaterEqual(len(write_result), 0.9 * i)
            speed1.append(len(write_result) / sum(write_result))

        self.info("Writing in MongoDB.")
        speed2 = []
        for i in processes:
            write_result = self.multi_process(target=self.mongo.write_string, process_number=i)
            self.assertGreaterEqual(len(write_result), 0.9 * i)
            speed2.append(len(write_result) / sum(write_result))

        self.info("Writing in Redis.")
        redis = Redis()
        speed3 = []
        for i in processes:
            write_result = self.multi_process(target=redis.write_string, process_number=i)
            self.assertGreaterEqual(len(write_result), 0.9 * i)
            speed3.append(len(write_result) / sum(write_result))

        self.info("Generating chart for writing speed for the three DataBases.")
        self.generate_chart(
            labels=processes,
            data1=speed1,
            data2=speed2,
            data3=speed3,
            title=title,
            yaxis=yaxis,
            xaxis=xaxis,
            output_file=output_file,
        )

    def test002_write_5_mb_string_nested_schema(self):
        """
        Test case for writing 5 MB of string in nested schema in parallel using mutli processes in BCDB and MongoDB.
        
        **Test scenario**
        #. Writing in BCDB.
        #. Writing in MongoDB.
        #. Generating chart for writing speed for the both DataBases.
        """
        processes = [1, 5, 10, 25, 50]
        title = "Writing 5 MB of string in nested schema on DataBase in parallel using multi processes (Higher speed is better)"
        yaxis = "Speed in MB/s"
        xaxis = "Number of processes"
        output_file = "nested_write_speed.html"

        self.info("Writing in BCDB.")
        speed1 = []
        for i in processes:
            write_result = self.multi_process(target=self.bcdb.write_nested, process_number=i)
            self.assertGreaterEqual(len(write_result), 0.9 * i)
            speed1.append(len(write_result) / sum(write_result))

        self.info("Writing in MongoDB.")
        speed2 = []
        for i in processes:
            write_result = self.multi_process(target=self.mongo.write_nested, process_number=i)
            self.assertGreaterEqual(len(write_result), 0.9 * i)
            speed2.append(len(write_result) / sum(write_result))

        self.info("Generating chart for writing speed for the both DataBases.")
        self.generate_chart(
            labels=processes,
            data1=speed1,
            data2=speed2,
            data3=None,
            title=title,
            yaxis=yaxis,
            xaxis=xaxis,
            output_file=output_file,
        )

    def test003_write_15_char_indexed_string(self):
        """
        Test case for writing 5 MB of string with 15 indexed character in parallel using mutli processes in BCDB, MongoDB and Redis.
        
        **Test scenario**
        #. Writing in BCDB.
        #. Writing in MongoDB.
        #. Generating chart for writing speed for the both DataBases.
        """
        processes = [1, 5, 10, 25, 50]
        title = "Writing 5 MB of string with 15 indexed character on DataBase in parallel using multi processes (Higher speed is better)"
        yaxis = "Speed in MB/s"
        xaxis = "Number of processes"
        output_file = "indexed_write_speed.html"

        self.info("Writing in BCDB.")
        speed1 = []
        for i in processes:
            write_result = self.multi_process(target=self.bcdb.write_indexed_string, process_number=i)
            self.assertGreaterEqual(len(write_result), 0.9 * i)
            speed1.append(len(write_result) / sum(write_result))

        self.info("Writing in MongoDB.")
        speed2 = []
        for i in processes:
            write_result = self.multi_process(target=self.mongo.write_indexed_string, process_number=i)
            self.assertGreaterEqual(len(write_result), 0.9 * i)
            speed2.append(len(write_result) / sum(write_result))

        self.info("Generating chart for writing speed for the both DataBases.")
        self.generate_chart(
            labels=processes,
            data1=speed1,
            data2=speed2,
            data3=None,
            title=title,
            yaxis=yaxis,
            xaxis=xaxis,
            output_file=output_file,
        )

    def test004_query(self):
        """
        Test case for querying in DataBase with change the number of objects.
        
        **Test scenario**
        #. Write random data in BCDB and mongoDB and set specific value (V1) in the middle of this data.
        #. Query BCDB for (V1) and calculate the time has been taken.
        #. Query MongoDB for (V1) and calculate the time has been taken.
        #. Generate chart for querying time for the both DataBases.
        """
        title = "Querying in DataBase with 15 indexed character with changing number of objects (Lower time is better)"
        yaxis = "Time in ms"
        xaxis = "Number of objects stored"
        output_file = "query.html"

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

            self.info("Query BCDB for (V1) and calculate the time has been taken.")
            model = self.bcdb.indexed_model
            time_start = time.time()
            target = model.find(name=name)
            time_stop = time.time()

            bcdb_time_taken = time_stop - time_start
            bcdb_query_time.append(bcdb_time_taken)
            self.assertTrue(target)
            self.assertEqual(target[0].text, text)

            self.info("Query MongoDB for (V1) and calculate the time has been taken.")
            time_start = time.time()
            target = StrIndexedDoc.objects(name=name)
            time_stop = time.time()

            mongo_time_taken = time_stop - time_start
            mongo_query_time.append(mongo_time_taken)
            self.assertTrue(target)
            self.assertEqual(target[0].text, text)

        self.info("Generate chart for querying time for the both DataBases")
        bcdb_query_time = [x * 1000 for x in bcdb_query_time]
        mongo_query_time = [x * 1000 for x in mongo_query_time]
        data_sizes = [100, 200, 500, 1000, 10000]
        self.generate_chart(
            labels=data_sizes,
            data1=bcdb_query_time,
            data2=mongo_query_time,
            data3=None,
            title=title,
            yaxis=yaxis,
            xaxis=xaxis,
            output_file=output_file,
        )
