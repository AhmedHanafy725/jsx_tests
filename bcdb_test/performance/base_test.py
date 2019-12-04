from unittest import TestCase
from uuid import uuid4
import multiprocessing
import os
import time 

from loguru import logger
from Jumpscale import j


class BaseTest(TestCase):
    LOGGER = logger
    LOGGER.add("BCDB_{time}.log")

    @classmethod
    def setUpClass(cls):
        cmd = """pkill redis-server
        sleep 1
        redis-server --port 6379"""
        cls.startup = j.servers.startupcmd.get("test_performance", cmd_start=cmd)
        cls.startup.start()
        os.system("service mongodb start")
        cls.wait_for_servers()

    @staticmethod
    def wait_for_servers():
        time.sleep(2)
        redis = j.sal.nettools.waitConnectionTest(ipaddr="localhost", port=6379, timeout=5)
        mongo = j.sal.nettools.waitConnectionTest(ipaddr="localhost", port=27017, timeout=5)
        if not redis or not mongo:
            raise RuntimeError("Servers didn't start")

    @classmethod
    def tearDownClass(cls):
        cls.startup.stop()
        j.sal.process.killProcessByName("redis-server")

    @staticmethod
    def random_string():
        return str(uuid4())[:10]

    @staticmethod
    def info(message):
        BaseTest.LOGGER.info(message)

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
