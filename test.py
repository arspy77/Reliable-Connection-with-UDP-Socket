from filepacket import FilePacketSender, FilePacketReciever

if __name__ == "__main__":
    sender = FilePacketSender("testImage.jpg", 0)
    reciever = FilePacketReciever("testImage2.jpg", 0)
    while not sender.is_done():
        packet = sender.send_packet()
        # print(packet)
        if reciever.recieve_packet(packet):
            ack = reciever.send_ack()
            sender.recieve_ack(ack)
    print("done")
