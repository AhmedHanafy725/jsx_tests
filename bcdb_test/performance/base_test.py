from unittest import TestCase
from uuid import uuid4
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

    def generate_chart(self, labels, data1, data2, title, yaxis, xaxis, output_file):
        chart = Charts()
        labels = labels
        legend1 = "MongDB"
        color1 = "rgb(0, 0, 255)"
        dataset1 = chart.generate_dataset(legend=legend1, data=data1, color=color1)

        legend2 = "BCDB"
        color2 = "rgb(255, 0, 0)"
        dataset2 = chart.generate_dataset(legend=legend2, data=data2, color=color2)

        datasets = [dataset1, dataset2]
        path = os.path.dirname(os.path.abspath(__file__))
        output_path = os.path.join(path, output_file)
        chart.generate_chart(
            labels=labels, datasets=datasets, title=title, yaxis=yaxis, xaxis=xaxis, output_path=output_path
        )
