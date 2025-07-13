import minimalmodbus 
import time
import logging

SENSOR_ADDRESS = 33
# SERIAL_PORT = '/dev/ttyUSB0'
SERIAL_PORT = 'COM4'  # Adjust this to your serial port
TEMP_ADDRESS = 2
HUMID_ADDRESS = 6

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

client = client_setup(SENSOR_ADDRESS)

def read_sensor_data():
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
    while True:
        temp, humid = read_sensor_data()
        if temp is not None and humid is not None:
            print(f"Temperature: {temp} °C, Humidity: {humid} %")
        else:
            print("Failed to read data.")
        time.sleep(2)  # Poll every 2 seconds

if __name__ == "__main__":
    main()