from flask import Blueprint, Response, json
from controllers.person import get_person

route_person = Blueprint('route_person', __name__)


@route_person.route('/person/<dni>')
def get_data(dni):
    data = get_person(dni)
    return Response(response=json.dumps(data), status=200, mimetype='application/json')
