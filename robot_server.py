import flask
from servo_mc import servo

app = flask.Flask(__name__)
app.config["DEBUG"] = True

servo_obj = servo()
@app.route('/', methods=['GET'])
def home():
    return "<h1>Robot framework.</p>"


@app.route('/find_button', methods=['GET'])
def find_button():
    return servo_obj.findButtonAngle()


app.run()
