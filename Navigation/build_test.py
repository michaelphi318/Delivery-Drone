from pyparrot.Bebop import Bebop
from threading import Thread
from pynput.keyboard import Key, KeyCode, Listener
from arrive import *
from gps import *
from avoidance import *
from sensor import *
from logger import *
import sys, os, time, datetime, traceback


def on_press(key):
    # print('{0} pressed'.format(key))
    pass

def on_release(key):
    global stop

    # print('{0} release'.format(key))
    if key == Key.esc:
        return False
    elif key == KeyCode.from_char("q"):
        bebop.safe_land(10)
        print("Emergeny landing protocol - disconnecting")
        bebop.disconnect()
        os._exit(1)
    elif key == KeyCode.from_char("p"):
        stop = True
    elif key == KeyCode.from_char("r"):
        stop = False

def readGPSFromFile():
    data = []
    fname = os.path.dirname(os.path.realpath(__file__)) + "/gps.txt"

    with open(fname, "r") as f:
        data = list(map(float, f.readlines()))

    return data[0], data[1]

def test():
    #---------------------Declare------------------------------
    lat, lon = readGPSFromFile()
    arriveThread = Arrive(bebop, lat, lon)
    # avoidance = Avoidance(bebop)
    threads = [arriveThread, arriveThread.gps]
    #----------------------------------------------------------

    try:
        with Listener(on_press=on_press, on_release=on_release) as listener:
            for thread in threads:
                # if isinstance(thread, (Arrive, GPS)):
                thread.start()
            
            while arriveThread.distance > 0.25:
                if stop:
                    arriveThread.pause()
                    bebop.loop_breaker = True
                    time.sleep(0.1)
                    bebop.loop_breaker = False
                else:
                    arriveThread.resume()
                    # bebop.loop_breaker = False

            for thread in threads:
                # if isinstance(thread, (Arrive, GPS)):
                thread.isTerminated = True
                thread.join()
                print("Thread %s terminated\n" % (thread.__class__.__name__))

            listener.join()
            sys.exit(0)
    except:
        print("Error in Main thread\n")
        traceback.print_exc()
        print("\n\nEmergency land the drone")
        bebop.safe_land(5)
        bebop.disconnect()
        os._exit(1)

# flat trim function
def calibrate():
    start_time = time.time()
    bebop.flat_trim(0)
    end_time = time.time()
    print("Flat trim finished after %.2f" % (end_time - start_time))

def connect():
    print("\nConnecting to the drone\n")
    success = bebop.connect(5)

    if not success:
        print("Connection failed\n")
        sys.exit(1)
        
    bebop.smart_sleep(2)
    calibrate()
    

if __name__ == "__main__":
    bebop = Bebop()
    stop = False    # test boolean
    path = os.path.dirname(os.path.realpath(__file__)) + "/log.txt"
    sys.stdout = Logger(path)
    sys.stderr = sys.stdout
    print(datetime.date.today().strftime("\n\n%d/%m/%Y"))
    print(datetime.datetime.now().strftime("%H:%M:%S"))

    connect()
    bebop.safe_takeoff(10)
    test()