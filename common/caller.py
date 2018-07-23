from common.db_manager import DbManager
from utils.parser import ShareParser, TradeParser


class Caller:
    @staticmethod
    def call_parsers(num_proc):
        db_manager = DbManager()
        db_manager.insert_stocks(stocks=ShareParser().call_parse(num_proc))                # Fill Stocks
        db_manager.insert_trades_and_traders(records=TradeParser().call_parse(num_proc))   # Fill Owners and Trades

    @staticmethod
    def clear_tables():
        DbManager().clear_tables()
