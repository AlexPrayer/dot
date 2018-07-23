from peewee import PrimaryKeyField
from peewee import CharField

from shared.database import BaseModel


class Share(BaseModel):
    class Meta:
        schema = 'dot'
        db_table = 'shares'

    id = PrimaryKeyField()
    code = CharField(unique=True)
    link = CharField()

    def as_dict(self):
        return {
            'id': self.id,
            'code': self.code,
            'link': self.link,
        }
