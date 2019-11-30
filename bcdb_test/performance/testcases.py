from .base_test import BaseTest
from .framework.bcdb import BCDB, TestBCDB
from .framework.mongodb import TestMonog, MongoDB

class PerformanceTest(BaseTest):
    def test001_write_1_mb(self):
        test = TestBCDB()
        model = BCDB.create_model()
        processes = [1, 5, 10, 15, 20, 30]
        title = "Writting 1 MB of string on DataBase in parallel using multi processes"
        yaxis = "Speed in MB/s"
        xaxis = "Number of processes"
        output_file = "speed_with_multi_processes.html"
        speed1 = []
        for i in processes:
            write_result = test.process(process_number=i, model=model)
            speed1.append(len(write_result) / sum(write_result))

        MongoDB()
        test = TestMonog()

        speed2 = []
        for i in range(1, 30, 5):
            write_result = test.process(process_number=i)
            speed2.append(len(write_result) / sum(write_result))

        self.generate_chart(labels=processes, data1=speed1, data2=speed2, title=title, yaxis=yaxis, xaxis=xaxis, output_file=output_file)