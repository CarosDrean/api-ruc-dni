from flask import Blueprint, Response, json
from controllers.contributor import get_contributor

route_contributor = Blueprint('route_contributor', __name__)


@route_contributor.route('/contributor/<ruc>')
def get_data(ruc):
    data = get_contributor(ruc)
    return Response(response=json.dumps(data), status=200, mimetype='application/json')
