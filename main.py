import minimalmodbus 
import time
import logging
from datetime import datetime
import simplejson as json
import paho.mqtt.client as mqtt


SENSOR_ADDRESS = 33
LOCATION = "outdoor"

# SERIAL_PORT = '/dev/ttyUSB0'
SERIAL_PORT = '/dev/tty.usbmodem56D11266251'  # Adjust this to your serial port
TEMP_ADDRESS = 2
HUMID_ADDRESS = 6

# MQTT connection details
mqtt_host = "mqtt.thingsboard.cloud"
mqtt_port = 1883
mqtt_topic = "v1/devices/me/telemetry"
mqtt_user = {
    "outdoor" : "E7wv4ZtwlIaUX6wTIARk",
    "indoor" : "H3QVwuWRByoFyHMrtfWv"
}

# MQTT Callback function when the client connects
def on_connect(client, userdata, flags, rc):
    print(f"Connected to MQTT server with result code {rc}")
    
# Function to upload data to MQTT
def upload_data_to_mqtt(location, timestamp, data, client):
    user_id = mqtt_user.get(location)

    if not user_id:
        print(f"No user ID found for sensor {location}")
        return

    # Prepare the payload
    payload = [
        {
            "ts": timestamp,  # Convert date to timestamp in milliseconds
            "values": {
                "temp": data["temp"],
                "humid": data["humid"]
            }
        }
    ]
    
    print("payload ===> ", payload)

    # Convert payload to JSON format
    payload_json = json.dumps(payload, use_decimal=True)
    
    # Publish the data to the MQTT server
    client.publish(mqtt_topic, payload_json, qos=1)
    print(f"Data for sensor {location} uploaded to MQTT: {payload_json}")


def client_setup(address):
    """Setup the Modbus client with the given address."""
    client = minimalmodbus.Instrument(SERIAL_PORT, address, debug=False)
    client.serial.baudrate = 9600
    client.serial.bytesize = 8
    client.serial.parity = minimalmodbus.serial.PARITY_NONE
    client.serial.stopbits = 1
    client.serial.timeout = 1
    client.mode = minimalmodbus.MODE_RTU
    client.clear_buffers_before_each_transaction = True
    return client

def read_sensor_data(client):
    """Read temperature and humidity from the sensor."""
    try:
        
        temperature = round(client.read_float(TEMP_ADDRESS), 2)
        humidity = round(client.read_float(HUMID_ADDRESS), 2)

        if temperature is None or humidity is None:
            raise ValueError("Received None from sensor")
        return temperature, humidity
    
    except Exception as e:
        print(f"Error reading sensor data: {e}")
        return None, None
    
def main():
    """Main function to continuously read sensor data."""
    print("Starting sensor polling...")
    client = client_setup(SENSOR_ADDRESS)

    mqtt_client = mqtt.Client()
    mqtt_client.on_connect = on_connect
    mqtt_client.username_pw_set(username=mqtt_user[LOCATION], password="")  # Change to appropriate user credentials for the meter

    # Connect to the MQTT broker
    mqtt_client.connect(mqtt_host, mqtt_port, 60)

    # Start the MQTT client in a separate thread
    mqtt_client.loop_start()

    while True:
        temp, humid = read_sensor_data(client)
        if temp is not None and humid is not None:
            print(f"Temperature: {temp} °C, Humidity: {humid} %")

            data = {
                "temp": temp,
                "humid": humid
            }

            timestamp = int(datetime.now().timestamp())*1000

            print(timestamp)

            # Upload data
            upload_data_to_mqtt(
                LOCATION,
                timestamp,
                data,
                mqtt_client
            )

        else:
            print("Failed to read data.")
        time.sleep(60)  # Poll every 2 seconds

if __name__ == "__main__":
    main()