import sys

import threading
import time
from datetime import datetime
import shutil
import json

import logging

import mysql.connector
from mysql.connector import errorcode

from ..tms import tmsconfig
from ..tms.teks_db import teks_db_api, teks_db_configure, teks_mysqldb_api
from ..tms.teks_db import teks_db_configure as db_tmsconfig, teks_mysqldb_handler as db_handler
from ..teks_libs import utils

from ..teks_libs.clock_timer import ClockTimer
from ..teks_libs.network_watch_dog import *

from ..tms.pojo.tms_msgs import TMSMsgs, TMSMsgDatas, _UNO_ID

from ..apis.mlbdata_apis import MLBDataApi
from ..apis.config_apis import ConfigApi
from ..apis.basic import _ApiConfig

class UnoMLBStatusCheck(ClockTimer):

    def __init__(self, stop_event, db_rlock, duration=3, ws=None, config=None):

        rlock = threading.RLock()

        ClockTimer.__init__(self,rlock,maxCount=duration, pill2kill=stop_event)
        self.setTimeoutCallback(self._get_mlb_status)

        self.__cnx = None

        self.__position_name = teks_db_configure.UNO_TOP_MODULE_STATS_TYPE[teks_db_configure.UNO_POSITION_INDEX].replace(" ", "_")
        self.__map_name = teks_db_configure.UNO_TOP_MODULE_STATS_TYPE[teks_db_configure.UNO_MAP_ID_INDEX].replace(" ", "_")

        self.init_db_conn()
        self.__config = config
        if not self.__config:
            self.init_db_conn()
            self.__serial_lock = threading.RLock()
            self.__db_lock = threading.RLock()            
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
        self.__serial_lock = self.__config.serial_lock
        self.__db_lock = self.__config.db_lock

        self.logger = self.__config.logger or logging.getLogger(__name__)

        self.__mlbdataApi = MLBDataApi(api_config=self.__config)
        self.__configApi = ConfigApi(api_config=self.__config)

        # self.__dbapi = teks_mysqldb_api
        # self.__ui_db = self.__dbapi.mysqldb_log_module()

        self.__api_path = "status/mlbdata"

        self.__thread_stop_event = stop_event
        self.__thread_rlock = rlock
        
        self.__thread_stop = False
        self.__suspend_flag = True

        self.__status = "offline"
        self.__lastStatus = ""

        self.__onChangeFunction = None
        self.__onDisplayFunction = None

        self.__TMSserver = self.__config.ws

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
          self.logger.error(__name__+": connect db: "+str(e))
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

    def send_tms_msg(self,msg, msg_type=tmsconfig.MSG_TYPE_STATUS, add_date=True, store_log=True):
        try:
            if store_log:
                if msg_type == tmsconfig.MSG_TYPE_STATUS:
                    self.logger.info(msg)
                else:
                    self.logger.warning(msg)

            str_now = utils.now_string()
            final_msg = msg
            if add_date:
                final_msg = str_now+": "+final_msg
            tms_msg_block = TMSMsgs(tmsconfig.CLIENT_ID,tmsconfig.CLIENT_NAME,tmsconfig.TMS_MSG_TYPE[msg_type],"",final_msg,str_now,"0")
            # self.logger.debug(tms_msg_block._to_json())
            self.logger.debug(str_now+": MLBData : Sending mlbdata status message")

            # jsonData = {
            #         "msg_type": tmsconfig.TMS_MSG_TYPE[msg_type],
            #         "client_id": tmsconfig.CLIENT_ID,
            #         "client_name": tmsconfig.CLIENT_NAME,
            #         "msg_data": final_msg
            #         }
            # print "sending..."+json.dumps(jsonData)
            if self.__TMSserver:
                self.__TMSserver._WS.send(json.dumps(tms_msg_block._to_json()))
        except Exception as e:
            self.logger.info(str(e))
            pass

    def _get_mlb_status(self):
        self.reset()

        mlb_data = None
        position_status = ""
        map_name_status = ""
        try:
            # with self.__db_rlock:
                recs = self.__mlbdataApi.collection(tmsconfig.UNO_ID)
                if recs and len(recs) > 0:
                    mlb_data = recs[0]
                recs = self.__configApi.load(tmsconfig.UNO_ID,self.__position_name)
                if recs:
                    position_status = recs[0].config_comd
                recs = self.__configApi.load(tmsconfig.UNO_ID,self.__map_name)
                if recs:
                    map_name_status = recs[0].config_comd
        except mysql.connector.Error as e:
            self.logger.error(__name__+": MLB data "+str(e))
        except Exception as e:
            self.logger.error(__name__+": MLB data "+str(e))

        if mlb_data:
            result = {
                "uno_id": str(tmsconfig.UNO_ID),
                "light": str(mlb_data.mlb_light),
                "humid": str(mlb_data.mlb_humid),
                "temper": str(mlb_data.mlb_temper),
                "map_id": str(mlb_data.mlb_map_id),
                "timestamp": str(mlb_data.mlb_ts),
                "position": str(position_status),
                "map_name": str(map_name_status),
            }

            self.logger.debug(json.dumps(result))

            if tmsconfig.PROD_RUN:
                if self.status and (self.status != self.__lastStatus):
                    msg_data = TMSMsgDatas(api_path=self.__api_path,func_type="B",data=result)
                    self.send_tms_msg(msg_data,msg_type=tmsconfig.MSG_TYPE_RUNTASK,add_date=False,store_log=False)
                    if self.onChangeFunction:
                        self.onChangeFunction()
            else:
                msg_data = TMSMsgDatas(api_path=self.__api_path,func_type="B",data=result)
                self.send_tms_msg(msg_data,msg_type=tmsconfig.MSG_TYPE_RUNTASK,add_date=False,store_log=False)
                if self.onChangeFunction:
                    self.onChangeFunction()

        self.start()
