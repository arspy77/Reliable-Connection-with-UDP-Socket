from filepacket import FilePacketSender, FilePacketReciever
import random

if __name__ == "__main__":
    sender = FilePacketSender("testImage.jpg", 0)
    reciever = FilePacketReciever("testImage2.jpg", 0)
    while not sender.is_done():
        packet = sender.send_packet()
        if bool(random.getrandbits(1)):
            packet = b''
        # print(packet)
        if reciever.recieve_packet(packet):
            ack = reciever.send_ack()
            if bool(random.getrandbits(1)):
                ack = b''
            if not sender.recieve_ack(ack):
                print("recieved bad ack")
        else:
            print("recieved bad packet")
    print("done")
