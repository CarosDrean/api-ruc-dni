from flask import Blueprint, Response, json
from controllers.person import get_person, get_person_card_immigration

route_person = Blueprint('route_person', __name__)


@route_person.route('/person/<document>')
def get_data(document):
    if len(document) > 8:
        data = get_person_card_immigration(document)
    else:
        data = get_person(document)
    return Response(response=json.dumps(data), status=200, mimetype='application/json')
