import threading
import socket
from filepacket import FilePacketSender
import time
import string
import random
import sys

class ThreadTimer(threading.Thread):
    def __init__(self, event, time, function, args):
        threading.Thread.__init__(self)
        self.stopped = event
        self.function = function
        self.args = args
        self.time = time

    def run(self):
        while not self.stopped.wait(self.time):
            self.function(self.args)

class Sender:
    def __init__(self, ip, port, filename, id):
        self._receiver_ip = ip
        self._receiver_port = port
        self._socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self._reader = FilePacketSender(filename, id)
        
    def send_message(self,MESSAGE):
        self._socket.sendto(MESSAGE, (self._receiver_ip, self._receiver_port))

    def run(self):
        while not(self._reader.is_done()):
            stop_flag = threading.Event()
            timer = ThreadTimer(stop_flag, 5, self.send_message, self._reader.send_packet())
            progresbar()
            self.send_message(self._reader.send_packet())
            timer.start()
            ack, _ = self._socket.recvfrom(1024)
            while not(self._reader.receive_ack(ack)):
                print("1")
                ack, _ = self._socket.recvfrom(1024)
            stop_flag.set()


def file_sender_thread(ip, port, filepath, id):
    sender = Sender(ip, port, filepath, id)
    sender.run()

def progresbar(): 
    for i in range(21):
        sys.stdout.write('\r')
        sys.stdout.write("[%-20s] %d%%" % ('='*i, 5*i))
        time.sleep(0.01)
    print()
if __name__ == "__main__":
    UDP_IP = input("Insert receiver IP   : ")
    UDP_PORT = int(input("Insert receiver port : "))
    n = int(input("Insert number of files to send: "))
    for i in range(n):
        filepath = input('Insert Filepath #' + str(i) + ': ')
        thread = threading.Thread(target=file_sender_thread, args=(UDP_IP,  UDP_PORT, filepath, i))
        thread.start()
    
