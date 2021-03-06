import time
from digitalio import DigitalInOut, Direction

_USE_PULSEIO = False
try:
    from pulseio import PulseIn

    _USE_PULSEIO = True
except ImportError:
    pass  # This is OK, we'll try to bitbang it!

__version__ = "0.0.0-auto.0"
__repo__ = "https://github.com/adafruit/Adafruit_CircuitPython_HCSR04.git"


class HCSR04:
    """Control a HC-SR04 ultrasonic range sensor.
    Example use:
    ::
        import time
        import board
        import adafruit_hcsr04
        sonar = adafruit_hcsr04.HCSR04(trigger_pin=board.D2, echo_pin=board.D3)
        while True:
            try:
                print((sonar.distance,))
            except RuntimeError:
                print("Retrying!")
                pass
            time.sleep(0.1)
    """

    def __init__(self, trigger_pin, echo_pin1, echo_pin2, *, timeout=0.1):
        """
        :param trigger_pin: The pin on the microcontroller that's connected to the
            ``Trig`` pin on the HC-SR04.
        :type trig_pin: microcontroller.Pin
        :param echo_pin: The pin on the microcontroller that's connected to the
            ``Echo`` pin on the HC-SR04.
        :type echo_pin: microcontroller.Pin
        :param float timeout: Max seconds to wait for a response from the
            sensor before assuming it isn't going to answer. Should *not* be
            set to less than 0.05 seconds!
        """
        self._timeout = timeout
        self._trig = trigger_pin
        self._trig.direction = Direction.OUTPUT

        if _USE_PULSEIO:
            self._echo1 = PulseIn(echo_pin1)
            self._echo1.pause()
            self._echo1.clear()
            self._echo2 = PulseIn(echo_pin2)
            self._echo2.pause()
            self._echo2.clear()
        else:
            self._echo1 = DigitalInOut(echo_pin1)
            self._echo1.direction = Direction.INPUT
            self._echo2 = DigitalInOut(echo_pin2)
            self._echo2.direction = Direction.INPUT

    def __enter__(self):
        """Allows for use in context managers."""
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Automatically de-initialize after a context manager."""
        self.deinit()

    def deinit(self):
        """De-initialize the trigger and echo pins."""
        self._trig.deinit()
        self._echo.deinit()

    @property
    def distance(self):
        """Return the distance measured by the sensor in cm.
        This is the function that will be called most often in user code. The
        distance is calculated by timing a pulse from the sensor, indicating
        how long between when the sensor sent out an ultrasonic signal and when
        it bounced back and was received again.
        If no signal is received, we'll throw a RuntimeError exception. This means
        either the sensor was moving too fast to be pointing in the right
        direction to pick up the ultrasonic signal when it bounced back (less
        likely), or the object off of which the signal bounced is too far away
        for the sensor to handle. In my experience, the sensor can detect
        objects over 460 cm away.
        :return: Distance in centimeters.
        :rtype: float
        """
        return self._dist_two_wire()  # at this time we only support 2-wire meausre
    
    
    def duration(self,timestamp,echo):
        if _USE_PULSEIO:
            echo.resume()
            while not self._echo:
                # Wait for a pulse
                if (time.monotonic() - timestamp) > self._timeout:
                    echo.pause()
                    raise RuntimeError("Timed out")
            self._echo.pause()
            pulselen = echo[0]
        else:
            # OK no hardware pulse support, we'll just do it by hand!
            # hang out while the pin is low
            while not echo.value:
                if time.monotonic() - timestamp > self._timeout:
                    raise RuntimeError("Timed out")
            timestamp = time.monotonic()
            # track how long pin is high
            while echo.value:
                if time.monotonic() - timestamp > self._timeout:
                    raise RuntimeError("Timed out")
            pulselen = time.monotonic() - timestamp
            pulselen *= 1000000  # convert to us to match pulseio
            
        return pulselen
    
    def _dist_two_wire(self):
        if _USE_PULSEIO:
            self._echo1.clear()  # Discard any previous pulse values
            self._echo2.clear()
        self._trig.value = True  # Set trig high
        time.sleep(0.00001)  # 10 micro seconds 10/1000/1000
        self._trig.value = False  # Set trig low

        pulselen = None
        timestamp = time.monotonic()
        pulselen1 = self.duration(timestamp,self._echo1)
        pulselen2 = self.duration(timestamp,self._echo2)
        
        if pulselen1 >= 65535 or pulselen2 >= 65535:
            raise RuntimeError("Timed out")
        
        distance1 = pulselen1 * 0.017
        distance2 = pulselen2 * 0.017
        # positive pulse time, in seconds, times 340 meters/sec, then
        # divided by 2 gives meters. Multiply by 100 for cm
        # 1/1000000 s/us * 340 m/s * 100 cm/m * 2 = 0.017
        return distance1,distance2
