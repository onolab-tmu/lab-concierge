'''
----------------------------------------------------------------------------
"THE BEER-WARE LICENSE" (Revision 42):
Robin Scheibler wrote this code.  As long as you retain this notice you
can do whatever you want with this stuff. If we meet some day, and you think
this stuff is worth it, you can buy me a beer in return.               Robin
----------------------------------------------------------------------------
'''
import urequests
import machine
import time
import network

# READ the settings
with open('config.json', 'r') as f:
    config = json.load(f)

# Get an "incoming-webhook" URL from your slack account. @see https://api.slack.com/incoming-webhooks
hook_url = config['slack_hook_url']

# WIFI related stuff
sta_if = network.WLAN(network.STA_IF)
wifi_credentials = (config['wifi']['SSID'], config['wifi']['pass'])
wifi_backoff_time_init = 2500
wifi_backoff_time = wifi_backoff_time_init
backoff_timer = machine.Timer(-1)
wifi_backing_off = False
def stop_backoff(t):
    global wifi_backing_off, sta_if
    if sta_if.isconnected():
        print('Backoff expired and WIFI is connected.')
    else:
        print('Backoff expired and WIFI is not connected. Retrying.')
    wifi_backing_off = False

# All messages
msg_coffee_ready = 'Coffee is ready. :coffee: :tada:'

# This is where we connected the button
button_coffee_ready = machine.Pin(22, machine.Pin.IN, machine.Pin.PULL_UP)
led = machine.Pin(2, machine.Pin.OUT)

led.value(1)


def concierge_to_slack(message, hook_url):
    '''
    A simple routine that posts to a slack channel as 'Concierge'
    '''

    print('Sending:', message)

    headers = {'content-type': 'application/json'}
    data = '{"text":"%s"}' % message
    resp = urequests.post(hook_url, data=data, headers=headers)

    print('Response:', resp.text)

    return resp.text == 'ok'

def blink(led_pin, n_times, on_time=500, off_time=500, on_value=True):
    '''
    Blink routine
    '''

    off_value = not on_value

    for n in range(n_times):
        led_pin.value(on_value)
        time.sleep_ms(on_time)
        led_pin.value(off_value)
        time.sleep_ms(off_time)

if __name__ == '__main__':

    while True:
        
        if sta_if.isconnected():

            # reset backoff to original value
            wifi_backing_off = False
            wifi_backoff_time = wifi_backoff_time_init

            # turn off LED when connected
            led.value(0)

            # Normal operations when connected
            if button_coffee_ready.value() == 0:
                ret = concierge_to_slack(msg_coffee_ready, hook_url)

                # blink and simple debounce
                blink(led, 1, on_time=200, off_time=100)

                # blink twice more if it fails
                if not ret:
                    blink(led, 2, on_time=200, off_time=100)

        elif not wifi_backing_off:

            # turn on LED to indicate we don't have a connection yet
            led.value(1)

            # turn on WIFI
            if not sta_if.active():
                sta_if.active(True)

            time.sleep_us(500)

            # check the wifi station is available
            print('Checking available networks')
            station_names = [a[0].decode() for a in sta_if.scan()]
            print(station_names)

            if wifi_credentials[0] in station_names:

                # it is there, try to connect
                print('connecting to {}...'.format(wifi_credentials[0]))
                sta_if.connect(*wifi_credentials)

            else:
                print('Error: can''t find SSID {}'.format(wifi_credentials[0]))

            # Back off a bit after trying to connect
            wifi_backing_off = True
            wifi_backoff_time *= 2  # exponential backoff
            backoff_timer.init(period=wifi_backoff_time, mode=machine.Timer.ONE_SHOT, callback=stop_backoff)

