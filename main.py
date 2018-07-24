import logging
from flask import Flask
from common.caller import Caller

from http_handlers import ShareHTTPHandler
from http_handlers import StocksHTTPHandler
from http_handlers import TradesHTTPHandler
from http_handlers import InsiderHTTPHandler
from http_handlers import AnalyticsHTTPHandler
from http_handlers import DeltaHTTPHandler

log = logging.getLogger(__name__)
logging_format = '%(levelname) -10s %(asctime)s %(name) -30s %(funcName) -50s %(lineno) -5d: %(message)s'
logging.basicConfig(level=logging.INFO, format=logging_format)


class Application:
    def __init__(self):
        app = Flask(__name__)
        self.create_application(app)

    def create_application(self, app):
        app.add_url_rule('/', view_func=ShareHTTPHandler.as_view('show_index'))
        app.add_url_rule('/api', view_func=ShareHTTPHandler().share_json)
        app.add_url_rule('/<share_code>', view_func=StocksHTTPHandler.as_view('show_stocks'))
        app.add_url_rule('/api/<share_code>', view_func=StocksHTTPHandler().stock_json)
        app.add_url_rule('/<share_code>/insider', view_func=TradesHTTPHandler.as_view('show_insider'))
        app.add_url_rule('/api/<share_code>/insider', view_func=TradesHTTPHandler().trades_json)
        app.add_url_rule('/<share_code>/insider/<insider_name>',
                         view_func=InsiderHTTPHandler.as_view('show_insider_name'))
        app.add_url_rule('/api/<share_code>/insider/<insider_name>',
                         view_func=InsiderHTTPHandler().insider_json)
        app.add_url_rule('/<share_code>/analytics/', view_func=AnalyticsHTTPHandler.as_view('show_analytics'))
        app.add_url_rule('/api/<share_code>/analytics/', view_func=AnalyticsHTTPHandler().analytics_json)
        app.add_url_rule('/<share_code>/delta', view_func=DeltaHTTPHandler.as_view('show_delta'))
        app.add_url_rule('/<share_code>/delta', view_func=DeltaHTTPHandler.delta_json)
        self.launch(app)

    @staticmethod
    def launch(app):
        app.run()


if __name__ == '__main__':
    print('Usage: ')
    print('Do you want to parse data? Or I can just run app for you.')
    print('Type \'yes\' if you want to parse data; Type \'no\' to just run app.')
    arg = input('yes/no\n')

    if arg == 'yes':
	    print('How many workers should parse the data?')
        caller = Caller()
        caller.clear_tables()
        num_proc = int(input())
        try:
            assert (isinstance(num_proc, int))
        except AssertionError:
            raise TypeError('Value should be integer.')
        caller.call_parsers(num_proc)
    elif arg == 'no':
        application = Application()
    else:
        raise ValueError("Input should be \'yes\' or \'no\'.")
