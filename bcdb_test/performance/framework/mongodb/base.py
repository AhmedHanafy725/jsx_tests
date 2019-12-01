from mongoengine import connect


class Base:
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.db_connect()

    def db_connect(self):
        connect(db="test", connect=False)
