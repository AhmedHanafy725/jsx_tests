from unittest import TestCase, skip
from uuid import uuid4
import random
import time

from Jumpscale import j
from parameterized import parameterized
from loguru import logger
from redis import ResponseError

LOGGER = logger
LOGGER.add("REDIS_{time}.log")


class TestRedisConfig(TestCase):

    startup = None
    redis_client = None

    @staticmethod
    def random_string():
        return str(uuid4())[:10]

    @staticmethod
    def info(message):
        LOGGER.info(message)

    def start_redis_server(self, port=None, password=False):
        if port:
            cmd = f"redis-server --port {port}"

        else:
            passwd = ""
            if password:
                passwd = "sed -i 's/# requirepass foobared/requirepass test/g' /tmp/redis.conf"
            cmd = f"""
            cp /etc/redis/redis.conf /tmp
            sed -i 's/port 6379/port 0/g' /tmp/redis.conf
            {passwd}
            echo "unixsocket /tmp/redis.sock" >> /tmp/redis.conf
            echo "unixsocketperm 775" >> /tmp/redis.conf
            redis-server /tmp/redis.conf
            """
        self.startup = j.servers.startupcmd.get("test_redis_config", cmd_start=cmd)
        self.startup.start()

    def tearDown(self):
        if self.startup:
            self.startup.stop()
            self.startup.delete()
        if self.redis_client:
            self.redis_client.delete()

        j.clients.redis._cache_clear()
        j.sal.process.killProcessByName("redis-server")
        super().tearDown()

    @parameterized.expand(["port", "unixsocket"])
    def test001_get_using_port_unixsocket(self, type):
        """TC564
        Test case for getting redis client using port/unixsocket.
        
        **Test scenario**
        #. Start redis server on port/unixsocket.
        #. Get redis client using port/unixsocket.
        #. Try to ping the server, should success.
        """
        self.info(f"Start redis server on {type}.")
        if type == "port":
            port = random.randint(10000, 11000)
            self.start_redis_server(port=port)
        else:
            self.start_redis_server()
        time.sleep(5)

        self.info(f"Get redis client using {type}.")
        name = self.random_string()
        if type == "port":
            self.redis_client = j.clients.redis_config.get(name=name, port=port)
        else:
            self.redis_client = j.clients.redis_config.get(name=name, unixsocket="/tmp/redis.sock", port=0, addr=None)
        cl = self.redis_client.redis

        self.info("Try to ping the server, should success.")
        self.assertTrue(cl.ping())

    @parameterized.expand([(False,), (True,)])
    def test002_set_password(self, password):
        """TC565
        Test case for getting redis client with/without password.
        
        **Test scenario**
        #. Start redis server on unixsocket with password.
        #. Try to get redis client with/without password, should success/fail.
        """
        self.info("Start redis server on unixsocket with password.")
        self.start_redis_server(password=True)
        time.sleep(5)

        self.info(f"Try to get redis client with password={password}")
        name = self.random_string()
        if password:
            self.redis_client = j.clients.redis_config.get(
                name=name, unixsocket="/tmp/redis.sock", port=0, addr=None, password_="test"
            )
            cl = self.redis_client.redis
            self.assertTrue(cl.ping())
        else:
            self.redis_client = j.clients.redis_config.get(name=name, unixsocket="/tmp/redis.sock", port=0, addr=None)
            with self.assertRaises(ResponseError) as e:
                cl = self.redis_client.redis
            self.assertIn("Authentication required", e.exception.args[0])

    @parameterized.expand([(True,), (False,)])
    def test003_set_patch(self, patch):
        """TC566
        Test case for getting redis client with/without setting patch.
        
        **Test scenario**
        #. Start redis server on a random port.
        #. Get redis client with/without setting patch.
        #. Try to set data on redis, should return "OK" in case of patching and "True" in case of no patching.
        """
        self.info("Start redis server on a random port.")
        port = random.randint(10000, 11000)
        self.start_redis_server(port=port)
        time.sleep(5)

        self.info(f"Get redis client with set_patch={patch}.")
        name = self.random_string()
        self.redis_client = j.clients.redis_config.get(name=name, port=port, set_patch=patch)
        cl = self.redis_client.redis
        self.assertTrue(cl.ping())

        self.info("Try to set data on redis")
        key = self.random_string()
        value = self.random_string()
        response = cl.set(name=key, value=value)
        if patch:
            self.assertEqual(response, b"OK")
        else:
            self.assertEqual(response, True)
        result = cl.get(name=key)
        self.assertEqual(result.decode(), value)

        # should return different value in case of another server is used.
        response = cl.delete(key)
        self.assertEqual(response, 1)

        result = cl.get(name=key)
        self.assertFalse(result)
