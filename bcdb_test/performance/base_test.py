from unittest import TestCase
from uuid import uuid4
import multiprocessing
import os

from loguru import logger

from .chart import Charts


class BaseTest(TestCase):
    LOGGER = logger
    LOGGER.add("BCDB_{time}.log")

    def setUp(self):
        pass

    def tearDown(self):
        pass

    @staticmethod
    def random_string():
        return str(uuid4())[:10]

    @staticmethod
    def info(message):
        BaseTest.LOGGER.info(message)

    def generate_chart(self, labels, data1, data2, data3, title, yaxis, xaxis, output_file):
        chart = Charts()
        labels = labels
        datasets = []

        legend1 = "BCDB(redis)"
        color1 = "rgb(0, 0, 255)"
        dataset1 = chart.generate_dataset(legend=legend1, data=data1, color=color1)
        datasets.append(dataset1)

        legend2 = "MongoBD"
        color2 = "rgb(255, 0, 0)"
        dataset2 = chart.generate_dataset(legend=legend2, data=data2, color=color2)
        datasets.append(dataset2)

        if data3 is not None:
            legend3 = "Redis"
            color3 = "rgb(0, 255, 0)"
            dataset3 = chart.generate_dataset(legend=legend3, data=data3, color=color3)
            datasets.append(dataset3)

        path = os.path.dirname(os.path.abspath(__file__))
        output_path = os.path.join(path, output_file)
        chart.generate_chart(
            labels=labels, datasets=datasets, title=title, yaxis=yaxis, xaxis=xaxis, output_path=output_path
        )

    def multi_process(self, target, process_number):
        manager = multiprocessing.Manager()
        write_result = manager.list()
        jobs = []
        for _ in range(process_number):
            process = multiprocessing.Process(target=target, args=(write_result,))
            jobs.append(process)
            process.start()

        for proc in jobs:
            proc.join()

        return write_result
