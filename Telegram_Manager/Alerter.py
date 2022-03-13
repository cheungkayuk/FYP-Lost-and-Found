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

    # each call to this function will append new log to message log file
    def sendToLog(self, imgFileName, className, checkpoint, direction, detectedTime):
        Log_Format = "%(levelname)s - %(message)s"
        now = datetime.datetime.now()
        currentTime = now.strftime("%Y-%m-%d %H:%M:%S")
        # log to a file called message.log
        logging.basicConfig(filename='message.log', format=Log_Format, level=logging.INFO)
        logger = logging.getLogger()
        
        content = "|"+str(currentTime)+"|"+imgFileName+","+className+","+checkpoint+","+direction+","+str(detectedTime)
        """
        Log format
            |<datetime to send message>|<image filename>,<classname>,<checkpoint>,<direction>,<detectedtime>
        INFO - |2022-03-13 19:59:07|abc.jpg,suitcase,A,A1,2022-03-13 18:59:07
        """
        try:
            logger.info(content)
            print("Logged", content,"to logfile!")
        except Exception as e:
            print(e)

    # read log contents froma file called message.log, then send the contents of each line
    def readAndSendFromLog(self):
        try:
            with open("message.log") as f:
                f = f.readlines()
        except Exception as e:
            print(e)
        
        for line in f:
            contents = line.split("|")
            # message in index 2, in form of <image filename>,<classname>,<checkpoint>,<direction>,<detectedtime>
            message = contents[2]
            # decompose message
            messages = message.split(",")
            image = messages[0]
            classname = messages[1]
            checkpoint = messages[2]
            direction = messages[3]
            detectedTime = messages[4]

            # send_msg()
            temp = f"Found {classname} at checkpoint {checkpoint} with direction {direction} at {detectedTime} "
            # send_msg(temp)
            print(f"Send message with send_msg: Found {classname} at checkpoint {checkpoint} with direction {direction} at {detectedTime} ")
            # send_img()
            #send_img(image)
            print(f"Send image with send_img: filename {image}\n")
    
    # sample to use with sendToLog() and readAndSendFromLog()
    #oneHourB4Now = (datetime.datetime.now() - datetime.timedelta(hours=1)).strftime("%Y-%m-%d %H:%M:%S")
    #sendToLog("abc.jpg", "suitcase", "A", "A1", oneHourB4Now)
    #readAndSendFromLog()


    def disconnect(self):
    # disconnecting the telegram session 
        self.kill()
        print("Disconnecting Alerter...\n")
