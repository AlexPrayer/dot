import simplejson as _json
from flask import render_template
from flask import request
from flask.views import MethodView

from shared.database.models import Stock
from shared.database.models import Share


class DeltaHTTPHandler(MethodView):
    def get(self, share_code):
        value = request.args.get('value')
        _type = request.args.get('type')
        x = self._get_data(value, _type, share_code)
        return render_template('delta.html', bounds=x)

    def delta_json(self, share_code):
        value = request.args.get('value')
        _type = request.args.get('type')
        return _json.dumps(self._get_data(value, _type, share_code))

    def _get_data(self, value, _type, share_code):

        data = [x.as_dict() for x in Stock.select().join(Share).where(Share.code == share_code)]
        dates = [x['date'] for x in data]
        values = [float("%.2f" % x[_type]) for x in data]
        index_bottom, index_top = self._get_indexes(values, float(value))
        return {'lower_bound': dates[index_bottom], 'upper_bound': dates[index_top]}

    @staticmethod
    def _get_indexes(lst, n):
        result = []
        for index, element in enumerate(lst, 0):
            for others in lst[index:]:
                if abs(element - others) >= n:
                    result.append([index, lst.index(others)])

        min_difference = float('inf')
        indexes = tuple()
        for x in result:
            sub = abs(x[0] - x[1])
            if sub < min_difference:
                min_difference = sub
                indexes = (x[0], x[1])
        return indexes
