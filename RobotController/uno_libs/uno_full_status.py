import sys

import threading
import time
from datetime import datetime
import shutil
import json

import logging

from ..tms import tmsconfig
from ..teks_libs import utils

from ..teks_libs.clock_timer import ClockTimer
from ..teks_libs.network_watch_dog import *

from ..tms.pojo.tms_msgs import TMSMsgs, TMSMsgDatas, _UNO_ID

class UnoFullStatusCheck(ClockTimer):

    def __init__(self, stop_event, rlock, ws=None, config=None):

        rlock = threading.RLock()
        # self.logger = logging.getLogger(__name__)

        ClockTimer.__init__(self,rlock,maxCount=5, pill2kill=stop_event)

        self.setTimeoutCallback(self.send_status)

        self.__config = config
        self.logger = self.__config.logger or logging.getLogger(__name__)

        self.__api_path = "fullstatus"

        self.__thread_stop_event = stop_event
        self.__thread_rlock = rlock
        
        self.__thread_stop = False
        self.__suspend_flag = True

        self.__status = "offline"
        self.__lastStatus = ""

        self.__onChangeFunction = None
        self.__onDisplayFunction = None

        self.__TMSserver = ws

        self.__uno_base_controller = None

        pass

    def suspend(self):
        with self.__thread_rlock:
            self.__suspend_flag = True
        
    def resume(self):
        with self.__thread_rlock:
            self.__suspend_flag = False

    @property
    def uno_base_controller(self):
        return self.__uno_base_controller

    @uno_base_controller.setter
    def uno_base_controller(self, value):
        self.__uno_base_controller = value
        pass    

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
            self.logger.debug(str_now+": Sending full status message")

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

    def send_status(self):
        # self.logger.debug("status_ok")
        self.reset()

        objList = self.uno_base_controller.basecontrollerapi.getFullStatus(None, tmsconfig.UNO_ID)
        if objList:
            msg_data = TMSMsgDatas(api_path=self.__api_path,func_type="B",data=objList)
            self.send_tms_msg(msg_data,msg_type=tmsconfig.MSG_TYPE_RUNTASK,add_date=False,store_log=False)

        self.start()
        pass


