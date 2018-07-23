from peewee import PrimaryKeyField
from peewee import DecimalField
from peewee import CharField
from peewee import DateTimeField
from peewee import ForeignKeyField

from shared.database import BaseModel
from shared.database.models import Trader
from shared.database.models import Share

from datetime import datetime


class Trade(BaseModel):
    class Meta:
        schema = 'dot'
        db_table = 'trades'

    id = PrimaryKeyField()
    last_date = DateTimeField(default=datetime.utcnow())
    transaction_type = CharField(null=True)
    shares_traded = DecimalField(max_digits=16, decimal_places=4, null=True)
    last_price = DecimalField(max_digits=16, decimal_places=4, null=True)
    shares_held = DecimalField(max_digits=16, decimal_places=4, null=True)
    insider = ForeignKeyField(Trader, related_name='insiders')
    share = ForeignKeyField(Share)

    def as_dict(self):
        return {
            'id': self.id,
            'last_date': str(self.last_date),
            'transaction_type': self.transaction_type,
            'shares_traded': self.shares_traded,
            'last_price': self.last_price,
            'shares_held': self.shares_held,
            'insider': self.insider.insider_name,
        }
