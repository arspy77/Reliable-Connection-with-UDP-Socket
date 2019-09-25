import threading
import socket
from filepacket import FilePacketSender
import time
import string
import random
import sys
import os
import math
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
        self.filesize = os.stat(filename).st_size
        self.partsize = 0
    def send_message(self,MESSAGE):
        self._socket.sendto(MESSAGE, (self._receiver_ip, self._receiver_port))
        self.partsize+= (sys.getsizeof(MESSAGE)-36)
        sys.stdout.write('\r')
        sys.stdout.write("[%-20s]" % ('='*int(self.partsize/self.filesize*20)))
        sys.stdout.write(str(int(self.partsize/self.filesize*100))+"%")
        sys.stdout.write("/100%")
    def run(self):
        while not(self._reader.is_done()):
            stop_flag = threading.Event()
            timer = ThreadTimer(stop_flag, 5, self.send_message, self._reader.send_packet())
            self.send_message(self._reader.send_packet())
            timer.start()
            ack, _ = self._socket.recvfrom(1024)
            while not(self._reader.recieve_ack(ack)):
                print("1")
                ack, _ = self._socket.recvfrom(1024)
            stop_flag.set()
        self.partsize=0
        


def file_sender_thread(ip, port, filepath, id):
    sender = Sender(ip, port, filepath, id)
    sender.run()

if __name__ == "__main__":
    UDP_IP = input("Insert reciever IP   : ")
    UDP_PORT = int(input("Insert reciever port : "))
    n = int(input("Insert number of files to send: "))
    for i in range(n):
        filepath = input('Insert Filepath #' + str(i) + ': ')
        thread = threading.Thread(target=file_sender_thread, args=(UDP_IP,  UDP_PORT, filepath, i))
        thread.start()
    