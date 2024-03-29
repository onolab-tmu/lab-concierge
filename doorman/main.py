"""
----------------------------------------------------------------------------
"THE BEER-WARE LICENSE" (Revision 42):
Robin Scheibler wrote this code.  As long as you retain this notice you
can do whatever you want with this stuff. If we meet some day, and you think
this stuff is worth it, you can buy me a beer in return.               Robin
----------------------------------------------------------------------------
"""
import json
import time

import machine
import network

from Slackbot import Slackbot

# READ the settings
with open("config.json", "r") as f:
    config = json.load(f)

# Get a bot token from your slack account. @see https://api.slack.com/apps
bot = Slackbot()

# We use a state machine to keep track of the door status
DOOR_OPEN = "The lab is open"
DOOR_CLOSED = "The lab is closed"

# WIFI related stuff
sta_if = network.WLAN(network.STA_IF)
wifi_ssid = config["wifi"]["SSID"]
wifi_pass = config["wifi"]["pass"]
wifi_backoff_time_init = 2500
wifi_backoff_time = wifi_backoff_time_init

# We want a backoff timer to try and reconnect to the network
backoff_timer = machine.Timer(-1)
wifi_backing_off = False


def stop_backoff(t):
    global wifi_backing_off, sta_if
    if sta_if.isconnected():
        print("Backoff expired and WIFI is connected.")
    else:
        print("Backoff expired and WIFI is not connected. Retrying.")
    wifi_backing_off = False


def bot_to_slack(message, bot):
    """
    A simple routine that posts to a slack channel as 'Onolab_bot'
    """

    print("Sending:", message)

    data = '{"text":"%s"}' % message
    resp = bot.send_message_to_channel("研究室開閉", data)

    print("Response:", "ok" if resp else "NG")

    return resp


def blink(led_pin, n_times, on_time=500, off_time=500, on_value=True):
    """
    Blink routine
    """

    off_value = not on_value

    for n in range(n_times):
        led_pin.value(on_value)
        time.sleep_ms(on_time)
        led_pin.value(off_value)
        time.sleep_ms(off_time)


def send_message_wrapper(msg):

    # can't do anything without network
    if not sta_if.isconnected():
        return

    # alert on slack
    ret = bot_to_slack(msg, bot)

    # blink and simple debounce
    blink(led, 1, on_time=200, off_time=100)

    # blink twice more if it fails
    if not ret:
        blink(led, 2, on_time=200, off_time=100)


door_status = 0


def door_action_callback(x):
    global door_status
    new_status = x()

    if new_status != door_status:
        if new_status == 0:
            send_message_wrapper(DOOR_OPEN)
        else:
            send_message_wrapper(DOOR_CLOSED)
        door_status = new_status


if __name__ == "__main__":

    ########
    # INIT #

    # This is where we connected the button
    door_switch = machine.Pin(22, machine.Pin.IN, machine.Pin.PULL_UP)
    # door_switch.irq(handler=door_open_callback, trigger=machine.Pin.IRQ_FALLING)
    # It seems that due to a bug, the interrupt is triggered on both rising and falling
    # That is convenient for now.
    door_switch.irq(handler=door_action_callback, trigger=machine.Pin.IRQ_RISING)
    door_status = door_switch()

    # The LED indicates connectivity
    led = machine.Pin(2, machine.Pin.OUT)
    led.value(1)

    ########
    # LOOP #

    while True:

        if sta_if.isconnected():

            # reset backoff to original value
            wifi_backing_off = False
            wifi_backoff_time = wifi_backoff_time_init

            # turn off LED when connected
            led.value(0)

        elif not wifi_backing_off:

            # turn on LED to indicate we don't have a connection yet
            led.value(1)

            # turn on WIFI
            if not sta_if.active():
                sta_if.active(True)

            time.sleep_us(500)

            # check the wifi station is available
            print("Checking available networks")
            station_names = [a[0].decode() for a in sta_if.scan()]
            print(station_names)

            if wifi_ssid in station_names:

                # it is there, try to connect
                print("connecting to {}...".format(wifi_ssid))
                sta_if.connect(wifi_ssid, wifi_pass)

            else:
                print("Error: can" "t find SSID {}".format(wifi_ssid))

            # Back off a bit after trying to connect
            wifi_backing_off = True
            wifi_backoff_time *= 2  # exponential backoff
            backoff_timer.init(
                period=wifi_backoff_time,
                mode=machine.Timer.ONE_SHOT,
                callback=stop_backoff,
            )

        time.sleep_ms(1000)
