"""
This file will configure the red button and provide
some callback routines
"""
from machine import Pin, Timer

class DebouncedButton(object):

    backing_off = False
    do_action = False

    def __init__(self, pin_num, backoff_time_ms=1000, timer_id=-1):
        self.pin = Pin(pin_num, Pin.IN, Pin.PULL_UP)
        self.pin.irq(trigger=Pin.IRQ_FALLING, handler=self.button_callback)
        self.backoff_time_ms = backoff_time_ms
        self.timer = Timer(timer_id)

    def button_callback(self, p):
        '''
        This is the callback called when the button is pressed
        '''
        if not self.backing_off:
            self.backing_off = True
            self.do_action = True
            self.timer.init(
                    period=self.backoff_time_ms,
                    mode=Timer.ONE_SHOT,
                    callback=self.de_backoff
                    )

    def de_backoff(self, t):
        self.backing_off = False

    def check_action(self, callback, *args, **kwargs):
        '''
        This will call the user provided callback function when the button has been pressed
        '''
        if self.do_action:
            callback(*args, **kwargs)
            self.do_action = False
