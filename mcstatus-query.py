#!/usr/bin/python3
from decimal import Decimal

#Author:    Jason Paul 
#Email:     jasonpa@gmail.com

#Testing using mcstatus API to query Minecraft server

from mcstatus import MinecraftServer

server = MinecraftServer.lookup("minecraft.linuxtek.ca:25565")
status = server.status()
query = server.query()
players = int(status.players.online)
latency = round(Decimal(status.latency),2)

print("Server Ping: ",latency)
print("Number of Players: ",players)

if players > 0:
    print("List of Players:")
    for player in status.players.sample:
        print(player.name + "\n")

