from filepacket import FilePacketSender, FilePacketReciever
import random

if __name__ == "__main__":
    sender = FilePacketSender("testImage.jpg", 0)
    reciever = FilePacketReciever("testImage2.jpg", 0)
    while not sender.is_done():
        packet = sender.send_packet()
        if random.randrange(100) < 35:
            packet[4] = 255 - packet[2]
        # print(packet)
        if reciever.recieve_packet(packet):
            ack = reciever.send_ack()
            if not sender.recieve_ack(ack):
                print("recieved bad ack")
        else:
            print("recieved bad packet")
    print("done")
