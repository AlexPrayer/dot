import datetime
import logging
import time
import traceback

from shared.database.models import Share
from shared.database.models import Stock
from shared.database.models import Trader
from shared.database.models import Trade
from utils.config import config
from utils.config import trades_mapping as mapping
from utils.mapper import Mapper

log = logging.getLogger(__name__)
logging_format = '%(levelname) -10s %(asctime)s %(name) -30s %(funcName) -50s %(lineno) -5d: %(message)s'
logging.basicConfig(level=logging.INFO, format=logging_format)

# logger = logging.getLogger('peewee')
# logger.addHandler(logging.StreamHandler())
# logger.setLevel(logging.DEBUG)


class DbManager:

    def __init__(self):
        self._config = config.copy()
        self._mapping = mapping

    def insert_share(self, share_name):
        share_data = {
            'code': share_name,
            'link': self._config['BASE_URL'] + share_name + self._config['SHARES_SUFFIX'],
        }

        try:
            share = Share.get_or_create(**share_data)
        except Exception as e:
            log.error('Something went wrong during the insert operation!')
            raise 'Exception: %s' % traceback.format_exc(e)

        try:
            assert(share is not None)
        except AssertionError as e:
            log.error('No share found. No share created.')
            raise 'Share was not found, was not created. Exception: %s' % traceback.format_exc(e)

        return share[0].id      # Return share_id

    def insert_stocks(self, stocks):

        rows = Mapper.map_fields(Stock, stocks)
        for row in rows:
            row['date'] = self.date_to_timestamp(row['date'])

        try:
            Stock.insert_many(rows).execute()
        except Exception as e:
            log.error('Something went wrong during the insert operation!')
            raise 'Exception: %s' % traceback.format_exc(e)

    def insert_trades_and_traders(self, records):
        for record in records:
            for trade in record:
                trader_data = {}
                for key, value in self._mapping['trader'].items():
                    trader_data[key] = trade[int(value)]

                try:
                    trader = Trader.get_or_create(**trader_data)
                except Exception as e:
                    raise "Error creating trader record. Check data. Exception: %s" % traceback.format_exc(e)

                trader_id = trader[0].id

                trade_data = {}
                for key, value in self._mapping['trade'].items():
                    trade_data[key] = trade[int(value)]
                trade_data['owner'] = trader_id
                trade_data['last_date'] = self.date_to_timestamp(trade_data['last_date'])

                try:
                    Trade.create(**trade_data)
                except Exception as e:
                    raise "Error creating trade record. Check data. Exception: %s" % traceback.format_exc(e)

    @staticmethod
    def clear_tables():
        query = Trade.delete()
        query.execute()
        query = Trader.delete()
        query.execute()
        query = Stock.delete()
        query.execute()
        query = Share.delete()
        query.execute()

    @staticmethod
    def date_to_timestamp(date_):
        if len(date_.split('/')) > 1:
            date_ = time.strftime('%Y-%m-%d %H:%M', time.strptime(date_, '%m/%d/%Y'))
        elif len(date_.split(':')) > 1:
            today = datetime.datetime.now()
            parts = date_.split(':')
            today.replace(hour=int(parts[0]), minute=int(parts[1]))
            date_ = str(today)
        return date_