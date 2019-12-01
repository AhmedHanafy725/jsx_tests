from Jumpscale import j


class Base:
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.bcdb = self.create_bcdb()

    def create_bcdb(self):
        bcdb = j.data.bcdb.get("test")
        return bcdb
