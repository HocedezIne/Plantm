from repositories.DataRepository import DataRepository
from flask import Flask, jsonify, request
from flask_socketio import SocketIO
from flask_cors import CORS


import time
import datetime as dt
from datetime import datetime
import threading
from subprocess import check_output, call

from RPi import GPIO
from helpers.MCP3008 import Mcp
from helpers.LCD import LCD

GPIO.setwarnings(False)
GPIO.setmode(GPIO.BCM)

pump = 21
led = 18
mcp = Mcp(0,0)
GPIO.setup(pump, GPIO.OUT)
GPIO.setup(led, GPIO.OUT)
GPIO.output(pump, GPIO.LOW)
GPIO.output(led, GPIO.LOW)


app = Flask(__name__)
app.config['SECRET_KEY'] = 'Hier mag je om het even wat schrijven, zolang het maar geheim blijft en een string is'

socketio = SocketIO(app, cors_allowed_origins="*")
CORS(app)

def read_sensors_on_connect():
    # LDR value
            LDR = mcp.read_channel(0)
            LDR = round((100- LDR / 1023.0 * 100),2)
            print(f"ldr {LDR}%")

            # Water level
            lvl = mcp.read_channel(1)
            print(f"lvl {lvl}")
            
            # Soil moisture
            smoist = mcp.read_channel(2)
            smoist = round(smoist/1023.0 * 100,2)
            print(f"smoist {smoist}%")

            # Temperature
            temp = mcp.read_channel(3)
            temp = round((temp / 1023.0 * 3.3) * 1000 / 10,2)
            print(f"temp {temp}°C")

            socketio.emit('B2F_current_values', {'LDR': LDR, "lvl": lvl, "smoist": smoist, "temp":temp})


# THREADS
def log_sensors():
    try:
        print("Start inlezen sensoren")
        while True:
            # LDR value
            ldr = mcp.read_channel(0)
            ldr = round((100- ldr / 1023.0 * 100),2)
            print(f"ldr {ldr}%")
            DataRepository.log_measurement("LDR", ldr)

            ldr_reference_values = DataRepository.get_min_max("LDR")
            ldr_control = DataRepository.check_endtime("LED")

            if ldr_control["StopTime"] == None:
                if ldr > ldr_reference_values["maximumvalue"]:
                    GPIO.output(led, GPIO.LOW)
                    DataRepository.log_off_time("LED")
            elif ldr < ldr_reference_values["minimumvalue"]:
                measurement_id = DataRepository.get_last_measurement()
                GPIO.output(led, GPIO.HIGH)
                DataRepository.log_on_time(measurement_id["ID"], "LED")
                
            # Water level
            lvl = mcp.read_channel(1)
            print(f"lvl {lvl}")
            DataRepository.log_measurement("LEVEL", lvl)

            lvl_reference_values = DataRepository.get_min_max("LEVEL")
            lvl_control = DataRepository.check_endtime("WRES")

            if lvl_control["StopTime"] == None:
                if lvl > lvl_reference_values["minimumvalue"]:
                    DataRepository. log_off_time("WRES")
            elif lvl < lvl_reference_values["minimumvalue"]:
                measurement_id = DataRepository.get_last_measurement()
                DataRepository.log_on_time(measurement_id["ID"], "WRES")
            
            # Soil moisture
            smoist = mcp.read_channel(2)
            smoist = round(smoist/1023.0 * 100,2)
            print(f"smoist {smoist}%")
            DataRepository.log_measurement("BV", smoist)
            smoist_reference_values = DataRepository.get_min_max("BV")
            if smoist < smoist_reference_values["minimumvalue"]:
                measurement_id = DataRepository.get_last_measurement()
                GPIO.output(pump, GPIO.HIGH)
                DataRepository.log_on_time(measurement_id["ID"], "WP")
                time.sleep(3)
                GPIO.output(pump, GPIO.LOW)
                DataRepository.log_off_time("WP")

            # Temperature
            temp = mcp.read_channel(3)
            temp = round((temp / 1023.0 * 3.3) * 1000 / 10,2)
            print(f"temp {temp}°C")
            DataRepository.log_measurement("TEMP", temp)

            temp_reference_values = DataRepository.get_min_max("TEMP")
            temp_low_control = DataRepository.check_endtime("TLOW")
            temp_high_control = DataRepository.check_endtime("THIGH")

            if temp_low_control["StopTime"] != None and (temp < temp_reference_values["minimumvalue"]):
                measurement_id = DataRepository.get_last_measurement()
                DataRepository.log_on_time(measurement_id["ID"], "TLOW")
            elif temp_low_control["StopTime"] == None and (temp > temp_reference_values["minimumvalue"]) and (temp < temp_reference_values["maximumvalue"]):
                DataRepository.log_off_time("TLOW")
            elif temp_high_control["StopTime"] != None and (temp > temp_reference_values["maximumvalue"]):
                measurement_id = DataRepository.get_last_measurement()
                DataRepository.log_on_time(measurement_id["ID"], "THIGH")
            elif temp_high_control["StopTime"] == None and (temp > temp_reference_values["minimumvalue"]) and (temp < temp_reference_values["maximumvalue"]):
                DataRepository.log_off_time("THIGH")

            # Send to frontend
            socketio.emit('B2F_current_values', {'LDR': ldr, "lvl": lvl, "smoist": smoist, "temp":temp})

            time.sleep(1800)
    except KeyboardInterrupt as e:
        print(e)
    finally:
        mcp.closespi()
        print("Stop inlezen sensoren")

def display():
    rs = 16
    e = 20
    databits_list = [12,25,24,23,26,19,13,6]

    GPIO.setup(rs, GPIO.OUT)
    GPIO.setup(e, GPIO.OUT)
    for i in databits_list:
        GPIO.setup(i, GPIO.OUT)

    try:
        lcd = LCD(databits_list, rs, e)
        print("Start weergeven IP adressen")

        while True:
            lcd.clear_LCD()

            # ip adressen weergeven
            ips = str(check_output(['hostname', '--all-ip-addresses'])).strip("b'").strip(" \\n").split(" ")
            lcd.write_message(ips[0])
            if len(ips) > 1:
                lcd.change_cursor_position(0b10101000) # cursur op 2de lijn plaatsen
                lcd.write_message(ips[1])
            time.sleep(60)
    except KeyboardInterrupt as e:
        print(e)
    finally:
        print("Stop weergeven IP adressen")

log_sensors_thread = threading.Thread(target=log_sensors)
lcd_thread = threading.Thread(target=display)

log_sensors_thread.start()
lcd_thread.start()



# SOCKET IO
@socketio.on('connect')
def initial_connection():
    print('A new client connect')
    # Send to the client!
    endTime = datetime.today().strftime("%Y-%m-%d") + " 23:59:59"
    startTime = (datetime.today() - dt.timedelta(days=5)).strftime("%Y-%m-%d") + " 00:00:00"
    data = DataRepository.read_measurements(startTime, endTime)
    for row in data:
        row["DateTime"] = str(row["DateTime"])
    socketio.emit('B2F_data_measurements', {'data': data})
    read_sensors_on_connect()

@socketio.on('F2B_send_data')
def send_data(json):
    startTime = json["data"]["start"]
    endTime = json["data"]["end"]
    data = DataRepository.read_measurements(startTime, endTime)
    for row in data:
        row["DateTime"] = str(row["DateTime"])
    socketio.emit("B2F_requested_data", {'data': data})

@socketio.on("F2B_send_min_max")
def send_min_max(json):
    data = DataRepository.get_min_max(json["deviceid"])
    socketio.emit("B2F_min_max", {"data": data})

@socketio.on("F2B_get_all_min_max")
def send_all_min_max():
    data = DataRepository.get_all_min_max()
    socketio.emit("B2F_all_min_max", {"data": data})

@socketio.on("F2B_update_min_max")
def update_min_max(json):
    data = json["data"]
    for key in data:
        if data[key] == "":
            data[key] = None
    DataRepository.update_min_max(data["ldrMin"], data["ldrMax"], "LDR")
    DataRepository.update_min_max(data["smoistMin"], data["smoistMax"], "BV")
    DataRepository.update_min_max(data["tempMin"], data["tempMax"], "TEMP")
    DataRepository.update_min_max(data["lvlMin"], data["lvlMax"], "LEVEL")

@socketio.on("F2B_get_plantname")
def get_plantname():
    data = DataRepository.get_plantname()
    socketio.emit("B2F_plantname", {"name": data})

@socketio.on("F2B_update_plantname")
def update_plantname(json):
    DataRepository.update_plantname(json["name"])

@socketio.on("F2B_shutdown")
def shutdown():
    call("sudo shutdown -f now", shell=True)

if __name__ == '__main__':
    socketio.run(app, debug=False, host='0.0.0.0')