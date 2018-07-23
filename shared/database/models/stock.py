from peewee import PrimaryKeyField
from peewee import DecimalField
from peewee import DateTimeField
from peewee import ForeignKeyField

from shared.database import BaseModel
from shared.database.models import Share

from datetime import datetime


class Stock(BaseModel):
    class Meta:
        schema = 'dot'
        db_table = 'stocks'

    id = PrimaryKeyField()
    date = DateTimeField(default=datetime.utcnow())
    opened = DecimalField(max_digits=16, decimal_places=4)
    high = DecimalField(max_digits=16, decimal_places=4)
    low = DecimalField(max_digits=16, decimal_places=4)
    close_last = DecimalField(max_digits=16, decimal_places=4)
    volume = DecimalField(max_digits=16, decimal_places=4)
    share = ForeignKeyField(Share)

    def as_dict(self):
        return {
            'id': self.id,
            'date': str(self.date),
            'open': self.opened,
            'high': self.high,
            'low': self.low,
            'close_last': self.close_last,
            'volume': self.volume,
            'share_id': self.share_id,
        }
