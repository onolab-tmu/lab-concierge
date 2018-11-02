'''
This file will configure the red button and provide
some callback routines
'''
import machine
import time

# initialize the red button
button_trig_time = None
send_coffee_message = False

def button_callback(p):
    '''
    This is the callback called when the button is pressed
    '''
    global send_coffee_message, button_trig_time
    now = time.ticks_ms()
    if button_trig_time is None or (now - button_trig_time > 100):
        send_coffee_message = True
        button_trig_time = now

def button_action(callback, *args, **kwargs):
    '''
    This will call the user provided callback function when the button has been pressed
    '''
    global send_coffee_message
    if send_coffee_message:
        callback(*args, **kwargs)
        send_coffee_message = False

button_coffee_ready = machine.Pin(22, machine.Pin.IN, machine.Pin.PULL_UP)
button_coffee_ready.irq(trigger=machine.Pin.IRQ_FALLING, handler=button_callback)
