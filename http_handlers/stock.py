from flask import render_template
import simplejson as _json
from flask.views import MethodView
from shared.database.models import Share
from shared.database.models import Stock


class StocksHTTPHandler(MethodView):
    def get(self, share_code):
        stocks = self._get_data(share_code)
        return render_template('stocks.html', stocks=stocks, share_code=share_code)

    def stock_json(self, share_code):
        stocks = self._get_data(share_code)
        return _json.dumps(stocks)

    @staticmethod
    def _get_data(share_code):
        stocks = [x.as_dict() for x in
                  Stock.select()
                      .join(Share)
                      .where(
                      Share.code == share_code
                  )]
        return stocks

