"""
A watchdog timer
"""
import machine

class WatchDogTimer(object):

    def __init__(self, period, timer_id=-1):
        self.period = period
        self.timer = machine.Timer(timer_id)
        self._start()

    def _start(self):
        self.timer.init(
                period=self.period,
                mode=machine.Timer.ONE_SHOT,
                callback=self._reboot
                )

    def _stop(self):
        self.timer.deinit()

    def _reboot(self, o):
        machine.reset()
        
    def reset(self):
        self._stop()
        self._start()
