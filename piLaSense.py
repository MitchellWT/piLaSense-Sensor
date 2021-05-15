import adafruit_dht
import adafruit_bmp3xx
import board
import busio
import time
import atexit
import sys
import requests
from digitalio import DigitalInOut, Direction
from gpiozero import LED

# Collects data from sensors using adafruit functions
def collect_data(DHT22, BMP388):
    return [
        DHT22.temperature,
        DHT22.humidity,
        BMP388.temperature,
        BMP388.pressure,
        BMP388.altitude
    ]

def send_data(data, ledArr):
    # Creates a POST request to a desired API URL
    # and attaches the provided data. It also includes
    # a authorization header to provide the API token.
    request = requests.post('POST_ADDRESS', data = {
        'sensor_system_id': 'SENSOR_SYSTEM_ID',
        'dht22_temperature': str(data[0]),
        'dht22_humidity': str(data[1]),
        'bmp388_temperature': str(data[2]),
        'bmp388_pressure': str(data[3]),
        'bmp388_altitude': str(data[4])
    }, headers = {
        'Authorization': 'Bearer API_TOKEN'    
    })

    update_led(request, ledArr)

def update_led(request, ledArr):
    # Turns on green LED, turns off
    # all other LEDs
    if request.json() == 'green':
        ledArr['green'].on()
        ledArr['yellow'].off()
        ledArr['red'].off()
    # Turns on yellow LED, turns off
    # all other LEDs
    elif request.json() == 'yellow':
        ledArr['green'].off()
        ledArr['yellow'].on()
        ledArr['red'].off()
    # Turns on red LED, turns off
    # all other LEDs
    elif request.json() == 'red':
        ledArr['green'].off()
        ledArr['yellow'].off()
        ledArr['red'].on()
    # Turns off all LED when no request
    # response was provided
    else:
        for led in ledArr:
            led.off()

def terminate(DHT22):
    # Closes connection to DHT22 sensor
    DHT22.exit()

def main():
    # Define DHT22 sensor to GPIO 21
    DHT22 = adafruit_dht.DHT22(board.D21)

    # Defines all required supporting pins for the BMP388 
    # (supporting pins: GPIO 9, GPIO 10, GPIO 11). Input pin as GPIO 26.
    SPI = busio.SPI(board.SCK, board.MOSI, board.MISO)
    CS = DigitalInOut(board.D26)
    BMP388 = adafruit_bmp3xx.BMP3XX_SPI(SPI, CS)

    # Defines all LEDs. Color and GPIO list:
    #   GREEN  = GPIO 7
    #   YELLOW = GPIO 4
    #   RED    = GPIO 13
    ledArr = {'green': LED(7), 'yellow': LED(4), 'red': LED(13)}

    # Set BMP388 values, these are example defaults
    BMP388.pressure_oversampling = 8
    BMP388.temperature_oversampling = 2

    # Define script termination function using atexit
    atexit.register(terminate, DHT22=DHT22)
    
    # Infinite loop for collecting sensor data and sending
    # it to the remote server.
    while(True):
        try:
            data = collect_data(DHT22, BMP388)

            send_data(data, ledArr)

            time.sleep(2)
        
        # When script is cancelled using CONTROL + C
        except KeyboardInterrupt as error:
            sys.exit(0)

        # When exception arises, mostly called when
        # DHT22 sensor has buffer or wiring issues as sensor is
        # not very reliable.
        except Exception as error:
            print(error)

main()
