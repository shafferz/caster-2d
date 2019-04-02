import PodSixNet.Channel
import PodSixNet.Server

from time import sleep

class ClientChannel(PodSixNet.Channel.Channel):

    def Network(self, data):
        print(data)

class CasterServer(PodSixNet.Server.Server):

    channelClass = ClientChannel

    def Connected(self, channel, addr):
        print("New connection: ", channel)

print("Server starting...")
server = CasterServer()
while True:
    server.Pump()
    sleep(0.01)
