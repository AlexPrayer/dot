import peewee
from playhouse.shortcuts import dict_to_model
from playhouse.shortcuts import model_to_dict

import shared.config as config
import json
database = peewee.PostgresqlDatabase(
    database=config.DATABASE_NAME,
    host=config.DATABASE_HOST,
    port=config.DATABASE_PORT,
    user=config.DATABASE_USERNAME,
    password=config.DATABASE_PASSWORD,
)


class BaseModel(peewee.Model):
    class Meta:
        database = database

    def as_dict(self):
        return model_to_dict(self)

    def as_json(self):
        return json.dumps(model_to_dict(self))

    @classmethod
    def from_dict(cls, data):
        return dict_to_model(cls, data)

    @classmethod
    def from_json(cls, data):
        return dict_to_model(cls, json.loads(data))
