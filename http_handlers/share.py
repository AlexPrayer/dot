import simplejson as _json
from flask import render_template
from flask.views import MethodView

from shared.database.models import Share


class ShareHTTPHandler(MethodView):
    def get(self):
        return render_template('index.html', shares=self._get_data())

    def share_json(self):
        return _json.dumps(self._get_data())

    @staticmethod
    def _get_data():
        return [x.as_dict() for x in Share.select()]
