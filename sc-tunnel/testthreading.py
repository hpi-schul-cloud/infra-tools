import time
import datetime
import threading


class TestThreading(object):
    def __init__(self, api_server_host, api_server_port,stopper, interval=1):
        self.interval = interval

        self.thread = threading.Thread(target=self.run, args=(api_server_host,api_server_port,stopper))
        self.thread.daemon = True
        self.thread.start()

    def run(self,api_server_name, api_server_port, stopper):
        while True:
            # More statements comes here
            #print(datetime.datetime.now().__str__() + ' : Hello ' + api_server_name + 'on port: ' + api_server_port)
            if not stopper.is_set():
                stopper.wait(2)
                time.sleep(self.interval)
            else:
                break
stop = threading.Event()
tr = TestThreading('Hugo.egon.balder', '1188', stopper=stop)
time.sleep(1)
print(datetime.datetime.now().__str__() + ' : First output')
time.sleep(2)
print(datetime.datetime.now().__str__() + ' : Second output')
while True:
    try:
        name = input("Please enter your first name: ")
        #list.append(name)
        if name == '1188':
            stop.set()
            print("Thread terminated")
            break
        else:
            continue
    except TypeError:
        print("Digits only please.")
        continue
    except EOFError:
        print("Please input something....")
        continue# press Ctrl-C for stopping

