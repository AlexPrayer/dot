import simplejson as _json
from flask import render_template
from flask import request
from flask.views import MethodView
from peewee import JOIN

from shared.database.models import Stock
from shared.database.models import Share

import datetime


class AnalyticsHTTPHandler(MethodView):
    def get(self, share_code):
        _low, _high, _close, _open = self._get_data(share_code)
        return render_template('analytics.html', low=_low, high=_high, close=_close, open=_open)

    def analytics_json(self, share_code):
        return _json.dumps(self._get_data(share_code))

    def _get_data(self, share_code):
        date_from = datetime.datetime.strptime(request.args.get('date_from'), '%m/%d/%Y')
        date_to = datetime.datetime.strptime(request.args.get('date_to'), '%m/%d/%Y')
        data = [x.as_dict() for x in Stock.select()
            .join(Share, JOIN.INNER)
            .where(
            (Share.code == share_code) &
            (Stock.date.between(date_from, date_to))
        )]
        low = []
        high = []
        close = []
        open_ = []
        for x in data:
            low.append(x['low'])
            high.append(x['high'])
            close.append(x['close_last'])
            open_.append(x['open'])
        _low = self.difference(low)
        _high = self.difference(high)
        _close = self.difference(close)
        _open = self.difference(open_)
        return _low, _high, _close, _open

    @staticmethod
    def difference(lst):
        return max(lst) - min(lst)

