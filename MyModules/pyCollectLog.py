
'''
this is test code
today is 20181201

'''
import zmq
import time
import datetime
import sys
from multiprocessing import Process


def client(port=5151):
    context = zmq.Context()
    print("Connecting to server with port %s" % port)
    socket = context.socket(zmq.SUB)
    socket.connect("tcp://localhost:%s" % port)
    socket.setsockopt_string(zmq.SUBSCRIBE,"")
    while True:

        message = socket.recv().decode("utf8")
        time_now= datetime.datetime.now().strftime('%Y/%m/%d %H:%M:%S.%f')
        print('[' +time_now +']', message)


if __name__ == "__main__":
    # Now we can run a few servers
    client(1055)
    # Now we can connect a client to all these servers
    #Process(target=client, args=(5555,)).start()
