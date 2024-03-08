import socket as udps
import time
import datetime
import os
import sys
import json
import threading

class socketThread(threading.Thread):
    def __init__(self, threadID, name, UDP_HOST, UDP_PORT, opmode, textFilePath):
        threading.Thread.__init__(self)
        self.threadID = threadID
        self.name = name
        self.UDP_HOST = UDP_HOST
        self.UDP_PORT = UDP_PORT
        self.opmode = opmode
        self.textFilePath = textFilePath

        # Open server socket
        try:
            self.serverSocket = udps.socket(udps.AF_INET, udps.SOCK_DGRAM)
            if opmode == "receive":
                self.serverSocket.bind((self.UDP_HOST, self.UDP_PORT))
        except Exception as e:
            print("Problem with setting up socket.")
            print(e)

    def receive(self):
        serviceComms, serviceAddr = self.serverSocket.recvfrom(1024)
        serviceCommsStr = str(serviceComms, 'utf-8')
        serviceCommsStr = serviceCommsStr.strip()
        with open(self.textFilePath, "a") as textFile:
            tsepoch = time.time()
            timeStampNow = datetime.datetime.fromtimestamp(tsepoch).strftime('%Y.%m.%d %H:%M:%S:%f')
            serviceCommsStrTS = str(timeStampNow) + '\t' + serviceCommsStr + '\t' + str(serviceAddr[0])
            textFile.write(serviceCommsStrTS + "\n")
        print(serviceCommsStrTS)

    def transmit(self):
        tsepoch = time.time()
        self.serverSocket.sendto("Text ".encode('utf-8') + str(datetime.datetime.fromtimestamp(tsepoch).strftime('%Y.%m.%d %H:%M:%S:%f')).encode('utf-8'), (self.UDP_HOST, self.UDP_PORT))
        print("Data sent at " + str(datetime.datetime.fromtimestamp(tsepoch).strftime('%Y.%m.%d %H:%M:%S:%f')))
        time.sleep(1)

    def run(self):
        print("Starting socket thread.")
        try:
            while True:
                if self.opmode == "receive":
                    self.receive()
                elif self.opmode == "transmit":
                    self.transmit()

        except Exception as e:
            print("Problem with main loop - reading/sending data from socket, printing them in the terminal or saving to file.")
            print(e)

if __name__ == "__main__":
    # Read json
    try:
        with open(os.path.join(sys.path[0], "config.json"), "r") as configFile:
            configData = json.load(configFile)
        print("JSON config read.")
    except Exception as e:
        print("Problem with json file.")
        print(e)

    # Timestamp
    tsepoch = time.time()
    timeStampNow = datetime.datetime.fromtimestamp(tsepoch).strftime('%Y%m%d_%H%M%S')

    # Address list
    try:
        UDP_HOST = configData["UDP_HOST"]
        print("UDP_HOST read.")
    except Exception as e:
        print("Problem with reading UDP_HOST.")
        print(e)

    # Port
    try:
        UDP_PORT_LISTEN_DATA = configData["UDP_PORT_LISTEN_SERVICE"]
        print("UDP_PORT_LISTEN_SERVICE read.")
    except Exception as e:
        print("Problem with reading UDP_PORT_LISTEN_SERVICE.")
        print(e)

    # TXT File with service data
    try:
        textFileServiceComm = configData["textFilePath"] + "serviceComm" + timeStampNow + ".txt"
        print("Service text file created.")
    except Exception as e:
        print("Problem with reading one of the paths.")
        print(e)

    # Start server
    serverThreadReceive = socketThread(1, "SocketThread", UDP_HOST, UDP_PORT_LISTEN_DATA, "receive", textFileServiceComm)
    serverThreadReceive.daemon = True
    serverThreadReceive.start()

    serverThreadTransmit = socketThread(1, "SocketThread", UDP_HOST, UDP_PORT_LISTEN_DATA, "transmit", textFileServiceComm)
    serverThreadTransmit.daemon = True
    serverThreadTransmit.start()

    try:
        while True:
            pass
    except KeyboardInterrupt:
        sys.exit()