import time
import machine
import dht, ds18x20, onewire

# The sensors
env_sense = None
coffee_sense = None
coffee_roms = None

# Initialize the temperature sensors
dat = machine.Pin(19)
coffee_sense = ds18x20.DS18X20(onewire.OneWire(dat))
coffee_roms = coffee_sense.scan()
if len(coffee_roms) == 0:
    print('Error: Temperature sensor not found!')
    coffee_sense = None
env_sense = dht.DHT22(machine.Pin(21))

def read_sensors():
    global env_sense, coffee_sense, coffee_roms

    ret = {}

    # Perform the measurement here
    if coffee_sense is not None:
        coffee_sense.convert_temp()
    env_sense.measure()

    time.sleep_ms(750)

    if coffee_sense is not None:
        ret['Coffee temperature'] = coffee_sense.read_temp(coffee_roms[0])

    ret['Room temperature'] = env_sense.temperature()
    ret['Room humidity'] = env_sense.humidity()

    return ret

