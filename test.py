from filereader import FilePacketReader, FilePacketWriter

sender = FilePacketReader("jyq5TU5.jpg", 0)
reciever = FilePacketWriter("jyq5TU5copy.jpg", 0)
i = 0
packet = sender.read(i)
while packet != b'':
    print(packet)
    if not reciever.write(packet):
        print('fail')
        break
    # packet = reciever.generate_ack()
    # if not sender.check_ack(packet):
    #     print('fail ack')
    #     break
    i += 1
    packet = sender.read(i)
