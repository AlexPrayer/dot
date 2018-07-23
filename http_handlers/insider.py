import simplejson as _json
from flask import render_template
from flask.views import MethodView

from shared.database.models import Share
from shared.database.models import Trade
from shared.database.models import Trader
from peewee import JOIN


class InsiderHTTPHandler(MethodView):
    def get(self, share_code, insider_name):
        return render_template('insider.html', trades=self._get_data(share_code, insider_name))

    def insider_json(self, share_code, insider_name):
        return _json.dumps(self._get_data(share_code, insider_name))

    @staticmethod
    def _get_data(share_code, insider_name):
        trades = [x.as_dict() for x in
                  Trade.select(Trade, Trader.insider_name)
                      .join(Trader, JOIN.INNER, on=(Trade.insider == Trader.id))
                      .switch(Trade)
                      .join(Share)
                      .where(
                      (Share.code == share_code) &
                      (Trader.insider_name == insider_name.strip())
                  )]
        return trades