import sys

import schedule

import threading
import time
from datetime import datetime
import shutil
import json

from ..tms import tmsconfig
from ..teks_libs import utils

import serial
from ..serial_tilt import serialconfig_tilt
from ..serial_tilt import conn_comm_utils_tilt as uno_cmd

from ..teks_libs.clock_timer import ClockTimer

from ..tms.pojo import tms_msgs
from ..tms.pojo.tms_msgs import TMSMsgs, TMSMsgDatas, _UNO_ID

from uno_tms_sdks.pojo.event_schedules import EventSchedules

class UnoEventScheduleCheck(ClockTimer):

    def __init__(self, stop_event, rlock, ws=None, config=None):

        rlock = threading.RLock()

        ClockTimer.__init__(self,rlock,maxCount=1, pill2kill=stop_event)

        self.setTimeoutCallback(self.check_status)

        self.__config = config
        self.logger = self.__config.logger or logging.getLogger(__name__)

        self.__api_path = ""

        self.__thread_stop_event = stop_event
        self.__thread_rlock = rlock
        
        self.__thread_stop = False
        self.__suspend_flag = True

        self.__status = ""
        self.__lastStatus = ""

        self.__onChangeFunction = None
        self.__onDisplayFunction = None

        self.__TMSserver = ws

        self.__event_schedules = None

        pass

    @property
    def schedules(self):
        return self.__event_schedules

    @schedules.setter
    def schedules(self, value):
        if value:
            with self.__thread_rlock:
                schedule.clear()
                self.__event_schedules = []
                self.append(value)

                # for evt in value:
                #     self.logger.debug("append events scheulde: "+str(evt["id"]))
                #     try:
                #         if evt["every"] == "hour" or \
                #             evt["every"] == "hours" or \
                #             evt["every"] == "minute" or \
                #             evt["every"] == "minutes" or \
                #             evt["every"] == "second" or \
                #             evt["every"] == "seconds" or \
                #             evt["every"] == "week" or \
                #             evt["every"] == "weeks":
                #             print "schedule.every("+str(evt["every_value"])+")."+str(evt["every"])+".do("+evt["do_type"]+" "+evt["do_value"]+" "+evt["do_params"]+")"
                #         elif evt["at_value"]:
                #             print "schedule.every("+str(evt["every_value"])+")."+str(evt["every"])+".at(\""+evt["at_value"]+"\").do("+evt["do_type"]+" "+evt["do_value"]+" "+evt["do_params"]+")"
                #         else:
                #             print "schedule.every("+str(evt["every_value"])+")."+str(evt["every"])+".do("+evt["do_type"]+" "+evt["do_value"]+" "+evt["do_params"]+")"
                #     except Exception as e:
                #         self.logger.debug(__name__+" : "+str(e))

                #     self.__event_schedules.append(EventSchedules._new_instance(evt))

                # need to clear the schedules and dynamically rebuild the schedules python codes
        pass    

    def job(self, input_params):
        params = input_params.split(":")
        task_type = params[0]
        task_values = params[1]
        task_params = params[2]
        pass

    def append(self, value):
        if value:
            with self.__thread_rlock:
                for evt in value:
                    self.logger.debug("append events scheulde: "+str(evt["id"]))
                    try:
                        if evt["every"] == "hour" or \
                            evt["every"] == "hours" or \
                            evt["every"] == "minute" or \
                            evt["every"] == "minutes" or \
                            evt["every"] == "second" or \
                            evt["every"] == "seconds" or \
                            evt["every"] == "week" or \
                            evt["every"] == "weeks":
                            schedule_job = "schedule.every("+str(evt["every_value"])+")."+str(evt["every"])+".do(self.job(\""+evt["do_type"]+":"+evt["do_value"]+":"+evt["do_params"]+"\"))"
                            print schedule_job
                        elif evt["at_value"]:
                            schedule_job = "schedule.every("+str(evt["every_value"])+")."+str(evt["every"])+".at(\""+evt["at_value"]+"\").do(self.job(\""+evt["do_type"]+":"+evt["do_value"]+":"+evt["do_params"]+"\"))"
                            print schedule_job
                        else:
                            schedule_job = "schedule.every("+str(evt["every_value"])+")."+str(evt["every"])+".do(self.job(\""+evt["do_type"]+":"+evt["do_value"]+":"+evt["do_params"]+"\"))"
                            print schedule_job
                    except Exception as e:
                        self.logger.debug(__name__+" : "+str(e))

                    self.__event_schedules.append(EventSchedules._new_instance(evt))
                    self.logger.debug(__name__+": schedule object - total #"+str(len(self.__event_schedules)))

                # need to clear the schedules and dynamically rebuild the schedules python codes
        pass    

    def send_tms_msg(self, msg_index, to_client_id, msg_data, msg_id="0"):
        try:
            if self.__TMSserver:
                str_now = utils.now_string()
                jsonData = {
                        tms_msgs._MSG_TYPE: tmsconfig.TMS_MSG_TYPE[msg_index],
                        tms_msgs._CLIENT_ID: tmsconfig.CLIENT_ID,
                        tms_msgs._CLIENT_NAME: tmsconfig.CLIENT_NAME,
                        tms_msgs._TO_CLIENT_ID: to_client_id,
                        tms_msgs._MESSAGE_ID: msg_id,
                        tms_msgs._MSG_DATA: msg_data
                        }
                self.logger.debug(str_now+": "+__name__+": send_tms_msg - "+jsonData[tms_msgs._MSG_DATA][tms_msgs._API_PATH])
                self.__TMSserver._WS.send(json.dumps(jsonData))
                return True
        except Exception as e:
            self.logger.error(str(e))
        return False

    def get_schedules(self):
        data = {
                    _UNO_ID:tmsconfig.UNO_ID,
              }
        final_msg = TMSMsgDatas(api_path="fulleventschedules",func_type="R",data=data)
        return self.send_tms_msg(tmsconfig.MSG_TYPE_RUNTASK, tmsconfig.TO_CLIENT_ID, final_msg._to_json())

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

        with self.__thread_rlock:
            schedule.run_pending()

        self.start()

        pass

    @property
    def is_suspend(self):
        return self.__suspend_flag

    # def start(self):
    #     self.start()


