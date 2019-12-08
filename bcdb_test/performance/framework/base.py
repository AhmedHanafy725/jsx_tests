import time

from Jumpscale import j


class Base:
    def __init__(self, data_size, **kwargs):
        self.string_model = None
        self.indexed_model = None
        self.nested_model = None
        self.data_size = data_size

    def write_string(self, write_result):
        text = j.data.idgenerator.generateXCharID(self.data_size)
        string_obj = self.create_obj(self.string_model)
        string_obj.text = text

        write_time = self.calculate_write_time(string_obj)
        # write_result.append(write_time)
        # return write_time
        write_result.put(write_time)

    def write_nested(self, write_result):
        text = j.data.idgenerator.generateXCharID(self.data_size)
        string_obj = self.create_obj(self.string_model)
        string_obj.text = text
        string_obj.save()
        nested_obj = self.create_obj(self.nested_model)
        nested_obj.string_obj = string_obj

        write_time = self.calculate_write_time(nested_obj)
        write_result.append(write_time)

    def write_indexed_string(self, write_result):
        text = j.data.idgenerator.generateXCharID(self.data_size)
        name = j.data.idgenerator.generateXCharID(15)
        indexed_obj = self.create_obj(self.indexed_model)
        indexed_obj.text = text
        indexed_obj.name = name

        write_time = self.calculate_write_time(indexed_obj)
        write_result.append(write_time)

    def create_obj(self, model):
        # this method should be overridden in all child classes
        pass

    def calculate_write_time(self, obj):
        write_start = time.time()
        obj.save()
        write_end = time.time()

        write_time = write_end - write_start
        return write_time
