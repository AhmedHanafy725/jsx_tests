import time

from parameterized import parameterized
from Jumpscale import j

from .base_test import BaseTest
from .framework.bcdb import TestBCDB
from .framework.mongodb import TestMongo, StrIndexedDoc, TwoFieldString
from .framework.redis import Redis


class PerformanceTest(BaseTest):
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
        title = "Writing 5 MB of string on DataBase in parallel using multi processes"
        yaxis = "Speed in MB/s"
        xaxis = "Number of processes"
        output_file = "speed_with_multi_processes.html"

        self.info("Writing in BCDB.")
        bcdb = TestBCDB(type="redis")
        speed1 = []
        for i in processes:
            write_result = self.multi_process(target=bcdb.write_string, process_number=i)
            self.assertGreaterEqual(len(write_result), 0.9 * i)
            speed1.append(len(write_result) / sum(write_result))

        self.info("Writing in MongoDB.")
        mongo = TestMongo()
        speed2 = []
        for i in processes:
            write_result = self.multi_process(target=mongo.write_string, process_number=i)
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
        title = "Writing 5 MB of string in nested schema on DataBase in parallel using multi processes"
        yaxis = "Speed in MB/s"
        xaxis = "Number of processes"
        output_file = "speed_with_multi_processes_nested.html"

        self.info("Writing in BCDB.")
        bcdb = TestBCDB()
        speed1 = []
        for i in processes:
            write_result = self.multi_process(target=bcdb.write_nested, process_number=i)
            self.assertGreaterEqual(len(write_result), 0.9 * i)
            speed1.append(len(write_result) / sum(write_result))

        self.info("Writing in MongoDB.")
        mongo = TestMongo()
        speed2 = []
        for i in processes:
            write_result = self.multi_process(target=mongo.write_nested, process_number=i)
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
        title = "Writing 5 MB of string with 15 indexed character on DataBase in parallel using multi processes"
        yaxis = "Speed in MB/s"
        xaxis = "Number of processes"
        output_file = "speed_with_multi_processes_indexed.html"

        self.info("Writing in BCDB.")
        bcdb = TestBCDB(type="redis")
        speed1 = []
        for i in processes:
            write_result = self.multi_process(target=bcdb.write_indexed_string, process_number=i)
            self.assertGreaterEqual(len(write_result), 0.9 * i)
            speed1.append(len(write_result) / sum(write_result))

        self.info("Writing in MongoDB.")
        mongo = TestMongo()
        speed2 = []
        for i in processes:
            write_result = self.multi_process(target=mongo.write_indexed_string, process_number=i)
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

    @parameterized.expand([(True, ), (False, )])
    def test004_query(self, index):
        """
        Test case for querying in DataBase with/without index.
        
        **Test scenario**
        #. Writing random data in BCDB and set sepecific value in the middle of this data(V1).
        #. Writing random data in MongoDB and set sepecific value in the middle of this data(V2).
        #. Query BCDB for (V1) and calculate the time has been taken.
        #. Query MongoDB for (V2) and calculate the time has been taken.
        """
        self.info("Writing data in BCDB and set sepecific value in the middle of this data(V).")
        data_size = 1000
        bcdb = TestBCDB(type="redis")
        for i in range(data_size):
            if i == data_size/2:
                name1 = j.data.idgenerator.generateXCharID(15)
                text1 = j.data.idgenerator.generateXCharID(1024)
                bcdb.write_two_field_string(index=index, key=name1, value=text1)
                continue
            bcdb.write_two_field_string(index=index)

        self.info("Query BCDB for (V1) and calculate the time has been taken.")
        if index:
            model = bcdb.indexed_model
        else:
            model = bcdb.two_field_model
        
        time_start = time.time()
        target = model.find(name=name1)
        time_stop = time.time()

        bcdb_time_taken = time_stop - time_start
        print(bcdb_time_taken)
        self.assertTrue(target)
        self.assertEqual(target[0].text, text1)
        
        self.info("Writing random data in MongoDB and set sepecific value in the middle of this data(V).")
        mongo = TestMongo(type="redis")
        for i in range(data_size):
            if i == data_size/2:
                name2 = j.data.idgenerator.generateXCharID(15)
                text2 = j.data.idgenerator.generateXCharID(1024)
                mongo.write_two_field_string(index=index, key=name2, value=text2)
                continue
            mongo.write_two_field_string(index=index)
        
        self.info("Query MongoDB for (V2) and calculate the time has been taken.")
        if index:
            doc = StrIndexedDoc
        else:
            model = TwoFieldString
        
        time_start = time.time()
        target = doc.objects(name=name2)
        time_stop = time.time()

        mongo_time_taken = time_stop - time_start
        print(mongo_time_taken)
        self.assertTrue(target)
        self.assertEqual(target[0].text, text2)

