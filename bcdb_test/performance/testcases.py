from .base_test import BaseTest
from .framework.bcdb.bcdb import TestBCDB
from .framework.mongodb.mongodb import TestMongo


class PerformanceTest(BaseTest):
    def test001_write_1_mb(self):

        processes = [1, 5, 10, 15, 20, 30]
        title = "Writting 1 MB of string on DataBase in parallel using multi processes"
        yaxis = "Speed in MB/s"
        xaxis = "Number of processes"
        output_file = "speed_with_multi_processes.html"

        mongo = TestMongo()
        speed1 = []
        for i in processes:
            write_result = self.multi_process(target=mongo.write, process_number=i)
            speed1.append(len(write_result) / sum(write_result))

        bcdb = TestBCDB()
        speed2 = []
        for i in processes:
            write_result = self.multi_process(target=bcdb.write, process_number=i)
            speed2.append(len(write_result) / sum(write_result))

        self.generate_chart(
            labels=processes, data1=speed1, data2=speed2, title=title, yaxis=yaxis, xaxis=xaxis, output_file=output_file
        )
