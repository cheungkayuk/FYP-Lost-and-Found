import sys

import threading
import time
from datetime import datetime
import shutil
import json
import os

import platform

import logging
import subprocess

import mysql.connector
from mysql.connector import errorcode

from ..tms import tmsconfig
from ..tms.teks_db import teks_db_api, teks_db_configure, teks_mysqldb_api
from ..tms.teks_db import teks_db_configure as db_tmsconfig, teks_mysqldb_handler as db_handler
from ..teks_libs import utils

from ..teks_libs.clock_timer import ClockTimer
from ..teks_libs.network_watch_dog import *

from ..tms.pojo.tms_msgs import TMSMsgs, TMSMsgDatas, _UNO_ID

from ..apis.config_apis import ConfigApi
from ..apis.basic import _ApiConfig
from ..pojo import configs

class UnoSoundManager(ClockTimer):

    def __init__(self, stop_event, db_rlock, device_idx, duration=3, ws=None, sound_file="", config=None):

        rlock = threading.RLock()

        ClockTimer.__init__(self,rlock,maxCount=duration, pill2kill=stop_event)
        self.setTimeoutCallback(self.__play_sound)

        self.__cnx = None

        self.__device_index = device_idx
        self.__device_name = teks_db_configure.UNO_TOP_MODULE_STATS_TYPE[self.__device_index].replace(" ", "_")

        self.init_db_conn()
        self.__config = config
        if not self.__config:
            self.init_db_conn()
            self.__config = _ApiConfig(
                tmsconfig.UNO_ID, None, application_id=tmsconfig.CLIENT_ID, 
                auth_token=None, 
                language="en", 
                db_conn=self.__cnx,
                ws=ws,
                tms_api=None,
                logger=logging.getLogger(__name__),
                serial_lock=self.__serial_lock,
                serial_port=None,
                db_lock = self.__db_lock
            )

        # self.__cnx = self.__config.db_conn

        self.logger = self.__config.logger or logging.getLogger(__name__)

        self.__configApi = ConfigApi(api_config=self.__config)

        self.__dbapi = teks_mysqldb_api
        self.__ui_db = self.__dbapi.mysqldb_log_module()

        self.__thread_stop_event = stop_event
        self.__thread_rlock = rlock
        
        self.__thread_stop = False
        self.__suspend_flag = True

        self.__status = "offline"
        self.__lastStatus = ""

        self.__onChangeFunction = None
        self.__onDisplayFunction = None

        self.__TMSserver = self.__config.ws

        self.__cur_path = os.path.dirname(os.path.abspath(__file__))
        self.__playerpath = self.__cur_path+"/fmedia/fmedia.exe"
        self.__sound_file = sound_file

        self.__volume = 1.0
        rec = self.__configApi.loadByID(tmsconfig.UNO_ID,config_id=teks_db_configure.UNO_MUSIC_VOLUME_INDEX+1)
        if rec and len(rec) > 0:
            self.__volume = float(rec[0].config_comd)
        else:
            self.volume = 1.0

        self.__isPlaying = False

        pass

    def exit(self):
        self.suspend()
        pass

    def init_db_conn(self):
        try:
          self.__cnx = db_handler.MySQLDB_Handler(self.logger)
        #   self.__cnx = mysql.connector.connect(**teks_db_configure.MYSQL_CONFIG)
        #   self.__cnx.start_transaction(isolation_level='READ COMMITTED')
        #   '''
        #   cur = self.cnx.cursor(buffered=False)
        #   cur.execute("SHOW STATUS LIKE 'Ssl_cipher'")
        #   self.logger.debug(cur.fetchone())
        #   cur.close()
        #   '''
        #   self.logger.debug(__name__+": "+self.__device_name+": connect db successfully")

        # except mysql.connector.Error as err:
        #     if err.errno == errorcode.ER_ACCESS_DENIED_ERROR:
        #         self.logger.error("Something is wrong with your user name or password")
        #     elif err.errno == errorcode.ER_BAD_DB_ERROR:
        #         self.logger.error("Database does not exist")
        #     else:
        #         self.logger.error(err)

        except Exception as e:
          self.logger.error("connect db: "+str(e))
          self.__conn = None
          self.__cnx = None

        pass

    def suspend(self):
        with self.__thread_rlock:
            self.__suspend_flag = True
        
    def resume(self):
        with self.__thread_rlock:
            self.__suspend_flag = False

    @property
    def status(self):
        return self.__status

    @status.setter
    def status(self, value):
        self.__status = value
        pass    

    @property
    def isPlaying(self):
        return self.__isPlaying

    @isPlaying.setter
    def isPlaying(self, value):
        self.__isPlaying = value
        pass    

    @property
    def volume(self):
        return self.__volume

    @volume.setter
    def volume(self, value):
        try:
            self.__volume = float(value)
            rec = self.__configApi.replaceValue(tmsconfig.UNO_ID,str(value),"",config_name=self.__device_name)
            # data = {
            #     configs._CONFIG_NAME:self.__device_name,
            #     configs._CONFIG_COMD:str(value),
            #     configs._CONFIG_T:""
            # }
            # rec = self.__configApi.replace(tmsconfig.UNO_ID,config_name=self.__device_name, data=data)
        except Exception as e:
            self.logger.debug(__name__+": "+str(e))
        pass    

    def volumneUp(self):
        vol = float(self.volume) + 0.1
        if vol > 1.0:
            vol = 1.0
        self.volume = str(vol)
        pass

    def volumneDown(self):
        vol = float(self.volume) - 0.1
        if vol < 0.0:
            vol = 0.0
        self.volume = str(vol)
        pass

    @property
    def onChangeFunction(self):
        return self.__onChangeFunction

    @onChangeFunction.setter
    def onChangeFunction(self, value):
        self.__onChangeFunction = value
        pass    

    @property
    def onDisplayFunction(self):
        return self.__onDisplayFunction

    @onDisplayFunction.setter
    def onDisplayFunction(self, value):
        self.__onDisplayFunction = value
        pass    

    @property
    def is_suspend(self):
        return self.__suspend_flag

    # def start(self):
    #     self.start()

    def __play_sound(self):
        self.reset()

        if self.is_suspend:
            with self.__thread_rlock:
                self.isPlaying = False
            pass
        else:
            # print(tmsconfig.UNO_ID)
            print(self.__device_name)
            try:
                # with self.__db_rlock:
                    recs = self.__configApi.load(tmsconfig.UNO_ID,self.__device_name)
                    print(recs)
                    if recs and len(recs) >= 1:
                        self.__volume = str(recs[0].config_comd)
                # tmp_status = str(self.__ui_db.get_top_module_config_by_key(self.__device_name))
            except mysql.connector.Error as e:
                # self.__ui_db = self.__dbapi.mysqldb_log_module()
                # tmp_status = str(self.__ui_db.get_top_module_config_by_key(self.__device_name))
                self.logger.error(__name__+": "+str(e))
            except Exception as e:
                self.logger.error(__name__+": "+str(e))


            if platform.system().upper() == "WINDOWS":
                # should wait for subprocess 
                # ret = subprocess.call([self.__playerpath,"--volume="+str(int(float(self.volume)*100)),"--notui","--background",self.__sound_file])
                ret = subprocess.call([self.__playerpath,"--volume="+str(int(float(self.volume)*100)),"--notui",self.__sound_file])
                pass
            else:
                #assume it is Mac.
                ret = subprocess.call(["afplay",self.__sound_file,"-v",str(self.volume)])
                pass
            # with self.__thread_rlock:
            #     if not self.isPlaying:
            #         print(self.volume)
            #         if platform.system().upper() == "WINDOWS":
            #             ret = subprocess.call([self.__playerpath,"--volume="+str(int(float(self.volume)*100)),"--notui","--background",self.__sound_file])
            #             pass
            #         else:
            #             #assume it is Mac.
            #             ret = subprocess.call(["afplay",self.__sound_file,"-v",str(self.volume)])
            #             pass
            #         self.isPlaying = True

        self.start()

