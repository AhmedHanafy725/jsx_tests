import time

import redis
from Jumpscale import j


class Redis:
    def __init__(self, data_size, **kwargs):
        super().__init__(**kwargs)
        self.redis = redis.Redis()
        self.data_size = data_size

    def write_string(self, write_result):
        text = j.data.idgenerator.generateXCharID(self.data_size)

        write_start = time.time()
        self.redis.hset(name="test.schema.1", key="text", value=text)
        write_end = time.time()

        write_time = write_end - write_start
        # write_result.append(write_time)
        # return write_time
        write_result.put(write_time)
