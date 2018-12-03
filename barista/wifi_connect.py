'''
Simple code to connect to the network
'''
import network
import time
import machine

# This is an enum (the module was not available in micropython)
class WifiState(object):
    CONNECTED = 0
    CONNECTING = 1
    NOT_CONNECTED = 2

class WifiConnection(object):

    def __init__(self, ssid, password):

        self.sta_if = network.WLAN(network.STA_IF)

        self.ssid = ssid
        self.password = password

        self.state = WifiState.NOT_CONNECTED

        self.backing_off = False
        self.backoff_time_init_ms = 2500
        self.backoff_time_ms = self.backoff_time_init_ms
        self.backoff_timer = machine.Timer(-1)

    def connect(self):

        if self.backing_off:
            return

        # turn on WIFI
        if not self.sta_if.active():
            self.sta_if.active(True)

        time.sleep_us(500)

        # check the wifi station is available
        print('Checking available networks')
        station_names = [a[0].decode() for a in self.sta_if.scan()]
        print(station_names)

        if self.ssid in station_names:
            # it is there, try to connect
            print('connecting to {}...'.format(self.ssid))
            self.sta_if.connect(self.ssid, self.password)
            self.state = WifiState.CONNECTING

        else:
            print('Error: can''t find SSID {}'.format(self.ssid))
            self.state = WifiState.NOT_CONNECTED

        # Back off a bit after trying to connect
        self.backing_off = True
        self.backoff_time_ms *= 2  # exponential backoff
        self.backoff_timer.init(period=self.backoff_time_ms, mode=machine.Timer.ONE_SHOT, callback=self.backoff_timer_expired)

    def connected(self):
        return self.state == WifiState.CONNECTED

    def keep_alive(self):
        if self.state == WifiState.CONNECTED:
            return

        elif self.state == WifiState.NOT_CONNECTED:

            if self.sta_if.isconnected():
                self.state = WifiState.CONNECTED
            else:
                self.connect()

        elif self.state == WifiState.CONNECTING:

            if self.sta_if.isconnected():
                self.state = WifiState.CONNECTED
                self.backing_off = False
                self.backoff_time_ms = self.backoff_time_init_ms
                print('Connection to network succeeded.')
                print('Network config:', self.sta_if.ifconfig())

    def backoff_timer_expired(self):

        if self.sta_if.isconnected():
            print('Backoff expired and WIFI is connected.')
        else:
            print('Backoff expired and WIFI is not connected. Retrying.')

        self.backing_off = False
