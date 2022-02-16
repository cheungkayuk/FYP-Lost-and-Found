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

class UnoInternetStatusCheck(ClockTimer):

    def __init__(self, stop_event, rlock, ws=None, config=None):

        rlock = threading.RLock()
        # self.logger = logging.getLogger(__name__)

        ClockTimer.__init__(self,rlock,maxCount=5, pill2kill=stop_event)

        self.internet_watch_dog = NetworkWatchDog("yahoo.com.hk",2.0,self.status_ok,self.status_fail)
        self.setTimeoutCallback(self.internet_watch_dog.have_ping)

        self.__config = config
        self.logger = self.__config.logger or logging.getLogger(__name__)

        self.__api_path = "status/internet"

        self.__thread_stop_event = stop_event
        self.__thread_rlock = rlock
        
        self.__thread_stop = False
        self.__suspend_flag = True

        self.__status = "offline"
        self.__lastStatus = ""

        self.__onChangeFunction = None
        self.__onDisplayFunction = None

        self.__TMSserver = ws

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
            self.logger.debug(str_now+": Sending Internet status message")

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

    def status_ok(self):
        # self.logger.debug("status_ok")
        self.reset()

        self.__lastStatus = self.status
        self.status = "online"
        if tmsconfig.PROD_RUN:
            if self.status and (self.status != self.__lastStatus):
                msg_data = TMSMsgDatas(api_path=self.__api_path,func_type="B",data={_UNO_ID:tmsconfig.UNO_ID,'status':self.__status})
                self.send_tms_msg(msg_data,msg_type=tmsconfig.MSG_TYPE_RUNTASK,add_date=False,store_log=False)
                if self.onChangeFunction:
                    self.onChangeFunction()

        else:
            msg_data = TMSMsgDatas(api_path=self.__api_path,func_type="B",data={_UNO_ID:tmsconfig.UNO_ID,'status':self.__status})
            self.send_tms_msg(msg_data,msg_type=tmsconfig.MSG_TYPE_RUNTASK,add_date=False,store_log=False)
            if self.onChangeFunction:
                self.onChangeFunction()

        self.start()
        pass

    def status_fail(self):
        # self.logger.debug("status_fail")
        self.reset()

        self.__lastStatus = self.status
        self.status = "offlne"
        if tmsconfig.PROD_RUN:
            if self.status and (self.status != self.__lastStatus):
                msg_data = TMSMsgDatas(api_path=self.__api_path,func_type="B",data={_UNO_ID:tmsconfig.UNO_ID,'status':self.__status})
                self.send_tms_msg(msg_data,msg_type=tmsconfig.MSG_TYPE_RUNTASK,add_date=False,store_log=False)
                if self.onChangeFunction:
                    self.onChangeFunction()
                    
        else:
            msg_data = TMSMsgDatas(api_path=self.__api_path,func_type="B",data={_UNO_ID:tmsconfig.UNO_ID,'status':self.__status})
            self.send_tms_msg(msg_data,msg_type=tmsconfig.MSG_TYPE_RUNTASK,add_date=False,store_log=False)
            if self.onChangeFunction:
                self.onChangeFunction()

        self.start()
        pass

