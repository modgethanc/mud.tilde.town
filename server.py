#!/usr/bin/env python
import sys, os
from twisted.internet import reactor, task
from twisted.internet.protocol import ServerFactory
from twisted.protocols.basic import LineOnlyReceiver

import time

from mud.login import Intro
from mud.core import *
from mud.game import *

print "\n\nstarting telnet server\n\n"

class MUDProtocol(LineOnlyReceiver):
    ## Connection object, will be hooked up to player object
    def __init__(self):
        self.__name__ = "MUDClient"
        self.player = False
        self.account = False
        self.character_idx = 0
        self.idle = 0

    def echo(self, mode):
        if mode == False:
          self.transport.write('\xff\xfb\x01')
        else:
          self.transport.write('\xff\xfc\x01')

    def clear(self):
        self.transport.write('\033[2J')

    def close_connection(self, message="disconnecting"):
        self.sendLine(message)
        self.transport.loseConnection()
        if self in self.factory.clientProtocols:
            self.factory.clientProtocols.remove(self)
        
    def save(self):
        if self.account:
          path = './save/accounts/'+self.account['name']+'.json'
          return data.save_json(self.account, path)
    
    def add_dialogue(self, dialogue):
        try:
            self.dialogue = dialogue
            res = dialogue.initial()
            call("start_dialogue", self, dialogue)
            if isinstance(res, (str, unicode)):
                    self.sendLine(res)
        except: 
            print "DIALOGUE EXCEPTION"
            raise

    def lineReceived(self, l):
        self.idle = 0
        line = parse.strip_escape_chars(l)
        if self.dialogue:
            try:
                res = self.dialogue.input(line)
                if res == False or self.dialogue.done == True:
                    call("end_dialogue", self, self.dialogue)
                    self.dialogue = False
                if isinstance(res, (str, unicode)):
                    self.sendLine(res)
            except: 
                print "DIALOGUE EXCEPTION"
                raise
        elif self.player:
            dispatch.call("player_input", self.player, line)
        self.transport.write(call("line_prompt", self.player))

    def sendLine(self, line):
        self.transport.write(line+"\r\n")

    def connectionMade(self):
        self.factory.clientProtocols.append(self)
        self.add_dialogue(Intro(self))
    
    def update(self, delta):
      self.idle += delta
      if self.idle > 400:
        dispatch.call("quit", self.player)
        self.close_connection("timed out")

    def enter_game(self, idx):
        self.character_idx = idx
        self.player = dispatch.call("player_enter_game", self, self.account["characters"][idx])




class ChatProtocolFactory(ServerFactory):

    protocol = MUDProtocol

    def __init__(self):
        self.clientProtocols = []
        self.last_time = time.time()
        loopingCall = task.LoopingCall(self.timeDisbatch)
        loopingCall.start(.5)

    def broadcast(self, mesg):
        #This should go to any state client
        for client in self.clientProtocols:
            client.sendLine(mesg)


    def timeDisbatch(self):
        delta = time.time() - self.last_time
        self.last_time = time.time()
        for client in self.clientProtocols:
          client.update(delta)
        call("update", delta)
        return True

def Main():
    port = 5071
    if len(sys.argv) > 1: 
        port = int(sys.argv[1])
    #data.game = Game()
    data.load(os.sep.join(['./mud/game']))
    call("init")
    factory = ChatProtocolFactory()
    reactor.listenTCP(port, factory)
    reactor.run()

if __name__== '__main__' :Main()
