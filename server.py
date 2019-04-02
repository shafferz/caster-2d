"""
Author: Zachary Shaffer
GitHub: @shafferz

The bare bones of a server in PodSixNet. This server runs, but has no
implemented functions for listening for or connecting to Clients, yet.

Honor Code: This work is mine unless otherwise cited. This code was created
with the examples in the source code for PodSixNet:
https://github.com/chr15m/PodSixNet
"""
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
