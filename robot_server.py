import flask
import servo_mc
import time

app = flask.Flask(__name__)
app.config["DEBUG"] = True

servo_obj = servo_mc.servo()
found_coordinates = (84, 107, 84, 10, 90, 90)
#servo_obj.robot.robot_coord((90, 120, 120, 30, 90, 90))
@app.route('/', methods=['GET'])
def home():
    return "<h1>Robot framework.</p>"


@app.route('/set_color/<color>', methods=['GET'])
def set_color(color):
    servo_obj.set_color(color)
    servo_obj.camera.get_colour_bound()
    return "Successfully Done"


@app.route('/get_color', methods=['GET'])
def get_color():
    return servo_obj.color


@app.route('/find_button', methods=['GET'])
def find_button():
    found_coordinates = servo_obj.findAngle()
    servo_obj.color_coordinates[servo_obj.color] = found_coordinates
    return str(found_coordinates)


@app.route('/reset', methods=['GET'])
def reset():
    servo_obj.robot.robot_coord((90, 120, 120, 30, 90, 90))
    return "reset  successful"


@app.route('/demo_side=<count>/<coordinates>/<color>', methods=['GET'])
def demo_side_button(count, coordinates, color):
    servo_obj.set_color(color)
    coordinate = coordinates.split(",")
    found_coordinates=((int(coordinate[0])), (int(coordinate[1])), (int(coordinate[2])), (int(coordinate[3])), (int(coordinate[4])), (int(coordinate[5])))
    alt_coordinates = (found_coordinates[0]-10, found_coordinates[1], found_coordinates[2], found_coordinates[3], found_coordinates[4], found_coordinates[5])
    alt_coordinates_press = (found_coordinates[0]-10, found_coordinates[1]-7, found_coordinates[2], found_coordinates[3], found_coordinates[4], found_coordinates[5])
    found_coordinates_press = (found_coordinates[0], found_coordinates[1]-7, found_coordinates[2], found_coordinates[3], found_coordinates[4], found_coordinates[5])
    for i in range(0, int(count)):
        servo_obj.robot.robot_coord(found_coordinates)
        servo_obj.robot.robot_coord(found_coordinates_press)
        servo_obj.robot.robot_coord(alt_coordinates)
        servo_obj.robot.robot_coord(alt_coordinates_press)
    servo_obj.robot.robot_coord(found_coordinates)
    return "Done"


@app.route('/demo_down=<count>/<coordinates>/<color>', methods=['GET'])
def demo_down_button(count, coordinates, color):
    servo_obj.set_color(color)
    coordinate = coordinates.split(",")
    found_coordinates=((int(coordinate[0])), (int(coordinate[1])), (int(coordinate[2])), (int(coordinate[3])), (int(coordinate[4])), (int(coordinate[5])))
    alt_coordinates = (found_coordinates[0], found_coordinates[1], found_coordinates[2], found_coordinates[3]+ 7, found_coordinates[4], found_coordinates[5])
    alt_coordinates_press = (found_coordinates[0], found_coordinates[1]-8, found_coordinates[2], found_coordinates[3]+7, found_coordinates[4], found_coordinates[5])
    found_coordinates_press = (found_coordinates[0], found_coordinates[1]-7, found_coordinates[2], found_coordinates[3], found_coordinates[4], found_coordinates[5])
    for i in range(0, int(count)):
        servo_obj.robot.robot_coord(found_coordinates)
        servo_obj.robot.robot_coord(found_coordinates_press)
        servo_obj.robot.robot_coord(alt_coordinates)
        servo_obj.robot.robot_coord(alt_coordinates_press)
    servo_obj.robot.robot_coord(found_coordinates)
    return "Done"


@app.route('/get_current_coord', methods=['GET'])
def get_current_coord():
    return str(servo_obj.robot.get_current_coord())


@app.route('/get_color_coord', methods=['GET'])
def get_color_coord():
    return str(servo_obj.color_coordinates)


@app.route('/set_angle=<coordinates>', methods=['GET'])
def set_angle(coordinates):
    coordinate = coordinates.split(",")
    servo_obj.robot.robot_coord(((int(coordinate[0])), (int(coordinate[1])), (int(coordinate[2])), (int(coordinate[3])), (int(coordinate[4])), (int(coordinate[5]))))
    return "Success"

app.run(host="0.0.0.0", port=5000, use_reloader=False)
