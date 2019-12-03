import time

import redis
from Jumpscale import j


class Redis:
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.redis = redis.Redis()

    def write_string(self, write_result):
        text = j.data.idgenerator.generateXCharID(1024 * 1024 * 5)

        write_start = time.time()
        self.redis.hset(name="test.schema.1", key="text", value=text)
        write_end = time.time()

        write_time = write_end - write_start
        write_result.append(write_time)
