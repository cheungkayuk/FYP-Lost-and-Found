import sys

import threading
import time
from datetime import datetime
import shutil
import json

import logging

from ..tms import tmsconfig
from ..teks_libs import utils

import serial
from ..serial_estop import serialconfig_estop
from ..serial_estop import conn_comm_utils_estop as uno_cmd

from ..teks_libs.clock_timer import ClockTimer

from ..tms.pojo.tms_msgs import TMSMsgs, TMSMsgDatas, _UNO_ID

class UnoEStopStatusCheck(ClockTimer):

    def __init__(self, stop_event, rlock, ws=None, config=None):

        rlock = threading.RLock()
        self.logger = logging.getLogger(__name__)

        ClockTimer.__init__(self,rlock,maxCount=5, pill2kill=stop_event)

        self.setTimeoutCallback(self.check_status)

        self.__config = config
        self.logger = self.__config.logger or logging.getLogger(__name__)

        if tmsconfig.ENABLE_SERIAL:
            self.logger.info("serial for ESTOP: "+str(serialconfig_estop.ESTOP_SERIAL_PORT)+" "+str(serialconfig_estop.ESTOP_SERIAL_BAUD))
            self.__ser_port = serial.Serial(serialconfig_estop.ESTOP_SERIAL_PORT, serialconfig_estop.ESTOP_SERIAL_BAUD, timeout=1)
        else:
            self.__ser_port = None

        self.__api_path = "status/estop"

        self.__thread_stop_event = stop_event
        self.__thread_rlock = rlock
        
        self.__thread_stop = False
        self.__suspend_flag = True

        self.__status = ""
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

    def check_status(self):
        self.reset()

        if tmsconfig.PROD_RUN:
            if self.__ser_port and self.__ser_port.isOpen():
                tmp_status = uno_cmd.getStatus(self.__ser_port)
                if tmp_status:
                    self.__lastStatus = self.status
                    self.status = tmp_status
                    if self.status and (self.status != self.__lastStatus):
                        #send tms msg
                        if self.__TMSserver:
                            str_now = utils.now_string()
                            # msg_data = TMSMsgDatas(api_path=self.__api_path,func_type="B",fields="{'status':'"+self.status+"'}")
                            msg_data = TMSMsgDatas(api_path=self.__api_path,func_type="B",data={_UNO_ID:tmsconfig.UNO_ID,'status':self.status})
                            tms_msg_block = TMSMsgs(tmsconfig.CLIENT_ID,tmsconfig.CLIENT_NAME,tmsconfig.TMS_MSG_TYPE[tmsconfig.MSG_TYPE_RUNTASK],"",msg_data,str_now,"0")
                            self.__TMSserver._WS.send(json.dumps(tms_msg_block._to_json()))

                        #call function if needed
                        if self.onChangeFunction:
                            self.onChangeFunction()
                    pass
        else:
            self.status = "0"
            # str_now = utils.now_string()
            # msg_data = TMSMsgDatas(api_path=self.__api_path,func_type="B",data={"status":self.status})
            # self.logger.debug(msg_data._to_json())
            # tms_msg_block = TMSMsgs(tmsconfig.CLIENT_ID,tmsconfig.CLIENT_NAME,tmsconfig.TMS_MSG_TYPE[tmsconfig.MSG_TYPE_RUNTASK],"",msg_data,str_now)
            # self.logger.debug(tms_msg_block._to_json())

            if self.__TMSserver:
                str_now = utils.now_string()
                msg_data = TMSMsgDatas(api_path=self.__api_path,func_type="B",data={_UNO_ID:tmsconfig.UNO_ID,"status":self.status})
                tms_msg_block = TMSMsgs(tmsconfig.CLIENT_ID,tmsconfig.CLIENT_NAME,tmsconfig.TMS_MSG_TYPE[tmsconfig.MSG_TYPE_RUNTASK],"",msg_data,str_now,"0")
                # self.logger.debug(tms_msg_block._to_json())
                self.logger.debug("Sending eStop status message")
                self.__TMSserver._WS.send(json.dumps(tms_msg_block._to_json()))

            if self.onChangeFunction:
                self.onChangeFunction()

        self.start()

        pass

    @property
    def is_suspend(self):
        return self.__suspend_flag

    # def start(self):
    #     self.start()

