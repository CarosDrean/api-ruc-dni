from flask import Flask

from routes.contributor import route_contributor
from routes.person import route_person

app = Flask(__name__)
app.register_blueprint(route_person)
app.register_blueprint(route_contributor)


@app.route('/')
def hello_world():
    return 'Welcome API ruc-dni'


if __name__ == '__main__':
    app.run(host='0.0.0.0')
