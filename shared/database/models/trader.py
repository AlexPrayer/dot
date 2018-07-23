from peewee import PrimaryKeyField
from peewee import CharField

from shared.database import BaseModel


class Trader(BaseModel):
    class Meta:
        schema = 'dot'
        db_table = 'traders'

    id = PrimaryKeyField()
    insider_name = CharField()
    relation = CharField()
    owner_type = CharField()

    def as_dict(self):
        return {
            'id': self.id,
            'insider_name': self.insider_name,
            'relation': self.relation,
            'owner_type': self.owner_type,
        }
