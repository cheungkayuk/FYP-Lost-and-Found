# importing all required libraries
from time import strftime
from time import sleep
import telebot
from telethon.sync import TelegramClient
from telethon.tl.types import InputMediaPoll, PeerChannel
from telethon import TelegramClient, sync, events
from telethon.tl.functions.messages import SendMessageRequest

from pathlib import Path  

import threading
import queue
import asyncio

from Tel_Info import *
import json
###########################################################

RESEND_NUM = 5
###########################################################

# get your api_id, api_hash, token
# from telegram as described above


class Alerter:
    def __init__(self, Receiver = {'api_id' : api_id, 'api_hash' : api_hash, 'token' : token, 'channel_id' : channel_id, 'phone' : phone}
    , session_name = username, map_only = False):
        #app info
        self.api_id = Receiver['api_id']
        self.api_hash = Receiver['api_hash']
        self.token = Receiver['token']
        self.channel_id = Receiver['channel_id']        
        # your phone number
        self.phone = Receiver['phone']

    #####################################################################
        try:
            self.receiver = PeerChannel(self.channel_id)

            # creating a telegram session and assigning
            # it to a variable client
        #     self.client = TelegramClient(session_name, self.api_id, self.api_hash)
            
        #     # connecting and building the session
        #     self.client.connect()

        # # in case of script ran first time it will
        # # ask either to input token or otp sent to
        # # number or sent or your telegram id 
        #     if not self.client.is_user_authorized():
            
        #         self.client.send_code_request(self.phone)
                
        #         # signing in the client
        #         self.client.sign_in(self.phone, input('Enter the code: '))
        except:
            raise Exception

        self.session_name = session_name
        self.on = True
        self.error = False    
        self.q = queue.Queue()
        self.t = threading.Thread(target=self._sender)
        self.t.daemon = True

        self.client = TelegramClient(self.session_name, self.api_id, self.api_hash)
        try:
            self.client.connect()
            if not self.client.is_user_authorized():
            
                self.client.send_code_request(self.phone)
                
                # signing in the client
                self.client.sign_in(self.phone, input('Enter the code: '))
        except:
            self.error = True
            self.on = False
            self.client.disconnect()
            raise Exception

    def _sender(self):
        print("_sender started\n")
        new_loop = asyncio.new_event_loop()
        asyncio.set_event_loop(new_loop)
        loop = asyncio.get_event_loop()
        
        # connecting and building the session
        
        while self.on:
            try:
                obj = self.q.get() 
            except queue.Empty:
                sleep(0.2)
                continue
            except Exception as e:
                print(e)
                continue
            for i in range(RESEND_NUM):
                try:
                    if (obj[0] == "msg"):
                        self.client(SendMessageRequest(self.receiver, obj[1]))
                    
                    elif obj[0] == "img":
                        self.client.send_file(self.receiver, obj[1])
                    print(f"_sender sent a {obj[0]}\n")
                    break
                except:
                    print("Fail from sending to telegram! Now Retry. \n\n")
                    sleep(1)
                if (i == RESEND_NUM - 1) : 
                    self.on = False
                    self.error = True
                    print(f"Fail to send message for {i} times! \n\n")
                    self.disconnect()

    def startsender(self):
        self.t.start()

    def kill(self):
        print("_sender is killed")
        self.on = False

    def wait_for_send(self, obj):
        self.q.put(obj)
    
    def send_img(self, img_path):
        self.client.send_file(self.receiver, img_path)

    def send_msg(self, msg):
        self.client(SendMessageRequest(self.receiver, msg))


    def disconnect(self):
    # disconnecting the telegram session 
        self.kill()
        print("Disconnecting Alerter...\n")
       