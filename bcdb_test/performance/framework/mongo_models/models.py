from mongoengine import fields, Document, connect


class StrDoc(Document):
    text = fields.StringField(required=False)
    meta = {"collection": "test.schema.1"}


class Nested(Document):
    string_obj = fields.ReferenceField(StrDoc)
    meta = {"collection": "test.nested.1"}


class StrIndexedDoc(Document):
    name = fields.StringField(required=False)
    text = fields.StringField(required=False)
    meta = {"collection": "test.index.1", "indexes": ["name"]}
