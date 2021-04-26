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

def collect_data(DHT22, BMP388):
    return [
        DHT22.temperature,
        DHT22.humidity,
        BMP388.temperature,
        BMP388.pressure,
        BMP388.altitude
    ]

def send_data(data, ledArr):
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
    if request.json() == 'green':
        ledArr['green'].on()
        ledArr['yellow'].off()
        ledArr['red'].off()

    elif request.json() == 'yellow':
        ledArr['green'].off()
        ledArr['yellow'].on()
        ledArr['red'].off()

    elif request.json() == 'red':
        ledArr['green'].off()
        ledArr['yellow'].off()
        ledArr['red'].on()

    else:
        for led in ledArr:
            led.off()

def terminate(DHT22):
    DHT22.exit()

def main():
    DHT22 = adafruit_dht.DHT22(board.D21)

    SPI = busio.SPI(board.SCK, board.MOSI, board.MISO)
    CS = DigitalInOut(board.D26)
    BMP388 = adafruit_bmp3xx.BMP3XX_SPI(SPI, CS)

    ledArr = {'green': LED(7), 'yellow': LED(4), 'red': LED(13)}

    BMP388.pressure_oversampling = 8
    BMP388.temperature_oversampling = 2

    atexit.register(terminate, DHT22=DHT22)
    
    while(True):
        try:
            data = collect_data(DHT22, BMP388)

            send_data(data, ledArr)

            time.sleep(2)
    
        except KeyboardInterrupt as error:
            sys.exit(0)

        except Exception as error:
            print(error)

main()
