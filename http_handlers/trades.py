import simplejson as _json
from flask import render_template
from flask.views import MethodView
from peewee import JOIN

from shared.database.models import Share
from shared.database.models import Trade
from shared.database.models import Trader


class TradesHTTPHandler(MethodView):
    def get(self, share_code):
        return render_template('trades.html', trades=self._get_data(share_code), share_code=share_code)

    def trades_json(self, share_code):
        return _json.dumps(self._get_data(share_code))

    @staticmethod
    def _get_data(share_code):
        trades = [x.as_dict() for x in
                  Trade.select(Trade, Trader.insider_name)
                      .join(Trader, JOIN.INNER, on=(Trade.insider == Trader.id))
                      .switch(Trade)
                      .join(Share)
                      .where(
                      (Share.code == share_code) &
                      (Trade.insider == Trader.id)
                  )]
        return trades