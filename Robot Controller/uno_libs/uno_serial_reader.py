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
from ..teks_libs import utils
from ..tms.teks_db import teks_db_configure, teks_mysqldb_api, teks_mysqldb_handler as db_handler

import serial
from ..serial_uno import serialconfig
from ..serial_uno import conn_comm_utils as uno_cmd

from ..teks_libs.clock_timer import ClockTimer

from ..tms.pojo.tms_msgs import TMSMsgs, TMSMsgDatas, _UNO_ID

from ..apis.config_apis import ConfigApi
from ..apis.basic import _ApiConfig
from ..pojo.configs import _CONFIG_ID,_UNO_ID,_CONFIG_NAME,_CONFIG_COMD,_CONFIG_T

class UnoSerialReader(ClockTimer):

    def __init__(self, stop_event, rlock, ws=None, config=None):

        clocktimer_rlock = threading.RLock()

        ClockTimer.__init__(self,clocktimer_rlock,maxCount=0.1, pill2kill=stop_event)
        self.setTimeoutCallback(self.check_status)

        if tmsconfig.ENABLE_SERIAL:
            if config and config.serial_port:
                self.__ser_port = config.serial_port
            else:
                self.logger.info(__name__+" serial for AGV: "+str(serialconfig.SERIAL_PORT)+" "+str(serialconfig.SERIAL_BAUD))
                self.__ser_port = serial.Serial(serialconfig.SERIAL_PORT, serialconfig.SERIAL_BAUD, timeout=1)
        else:
            self.__ser_port = None

        self.__conn = None
        self.__cnx = None
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
                serial_port=self.__ser_port,
                db_lock=self.__db_lock,
            )

        self.__serial_lock = self.__config.serial_lock
        self.__db_lock = self.__config.db_lock
        self.logger = self.__config.logger or logging.getLogger(__name__)

        self.__configApi = ConfigApi(api_config=self.__config)

        self.__api_path = "status/estop"

        self.__thread_stop_event = stop_event
        self.__thread_rlock = rlock
        
        self.__thread_stop = False
        self.__suspend_flag = True

        self.__status = ""
        self.__lastStatus = ""

        self.__onChangeFunction = None
        self.__onDisplayFunction = None
        self.__onPositionChangeFunction = None
        self.__onBatteryChangeFunction = None
        self.__onSwitchMapSuccessFunction = None

        self.__TMSserver = self.__config.ws

        # backward compatiable - store data for agvfront
        self.dbapi = teks_mysqldb_api
        with self.__db_lock:
            self.ui_db = self.dbapi.mysqldb_log_module()

        self.position_counter = 0
        self.battery_status = ""
        self.position_status = ""
        self.position_dec_status = ""

        pass

    def exit(self):
        if self.serial_conn:
            self.serial_conn.close()
        if self.__conn:
            self.__conn.close()
        if self.__cnx:
            self.__cnx.close()
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
        #   self.logger.debug(__name__+": connect db successfully")

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
    def serial_conn(self):
        return self.__ser_port

    @serial_conn.setter
    def serial_conn(self, value):
        self.__ser_port = value
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
    def onPositionChangeFunction(self):
        return self.__onPositionChangeFunction

    @onPositionChangeFunction.setter
    def onPositionChangeFunction(self, value):
        self.__onPositionChangeFunction = value
        pass    

    @property
    def onBatteryChangeFunction(self):
        return self.__onBatteryChangeFunction

    @onBatteryChangeFunction.setter
    def onBatteryChangeFunction(self, value):
        self.__onBatteryChangeFunction = value
        pass    

    @property
    def onSwitchMapSuccessFunction(self):
        return self.__onSwitchMapSuccessFunction

    @onSwitchMapSuccessFunction.setter
    def onSwitchMapSuccessFunction(self, value):
        self.__onSwitchMapSuccessFunction = value
        pass    

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
            self.logger.debug(str_now+": Sending "+str(self.__device_name)+" status message")

            # jsonData = {
            #         "msg_type": tmsconfig.TMS_MSG_TYPE[msg_type],
            #         "client_id": tmsconfig.CLIENT_ID,
            #         "client_name": tmsconfig.CLIENT_NAME,
            #         "msg_data": final_msg
            #         }
            # print "sending..."+json.dumps(jsonData)
            if self.__TMSserver:
                self.__TMSserver._WS.send(json.dumps(tms_msg_block))
        except Exception as e:
            self.logger.error(str(e))
            pass

    def check_status(self):
        self.reset()

        if tmsconfig.PROD_RUN:
            # with self.__serial_lock:
                if self.__ser_port and self.__ser_port.isOpen():
                    tmp_status, self.cmd_num, self.out_msg = uno_cmd.getNaviStatus(self.__ser_port)
                    if tmp_status:
                        self.logger.debug("current UNO status: "+tmp_status+" "+self.cmd_num+" "+self.out_msg)
                        if self.cmd_num == "03":
                            self.__lastStatus = self.__status
                            self.__status = tmp_status
                            # if self.__status and (self.__status != self.__lastStatus):
                            self.logger.debug("changed UNO status: from "+self.__lastStatus+" to "+self.__status)
                            self.__configApi.update(
                                tmsconfig.UNO_ID,
                                teks_db_configure.UNO_TOP_MODULE_STATS_TYPE[teks_db_configure.UNO_NAVI_STATUS_INDEX].replace(" ", "_"),
                                data={_CONFIG_COMD:str(self.__status),_CONFIG_T:"a"}
                                )
                            if self.onChangeFunction:
                                self.logger.debug("calling change function")
                                self.onChangeFunction()

                    else:
                        isLocationStatus = uno_cmd.is_LocationStatus(self.out_msg)
                        isBatteryStatus = uno_cmd.is_BatteryStatus(self.out_msg)
                        isSwitchMapSuccessStatus = uno_cmd.is_SwitchMapSuccessStatus(self.out_msg)
                        isObstacle = uno_cmd.is_Obstacle(self.out_msg)
                        
                        if isLocationStatus:
                            self.logger.debug("isLocationStatus")
                            results = isLocationStatus
                            if results and len(results) > 0:
                                #store results into database based on mapid and routeid
                                ts = ""+str(utils.gen_timestamp())
                                # self.ui_db.set_top_module_location(results[0]+str(ts),results[1]+str(ts),results[2]+str(ts),results[3]+str(ts),str(ts))
                                x_value = str(utils.get_corrd_in_dec(results[0]))
                                y_value = str(utils.get_corrd_in_dec(results[1]))
                                a_value = str(utils.get_corrd_in_dec(results[2]))
                                w_value = str(utils.get_corrd_in_dec(results[3]))
                                # self.logger.debug("set top module locaiton: "+x_value+" "+y_value+" "+a_value+" "+w_value)

                                # store the data for agvfront
                                self.ui_db.set_top_module_location(x_value,y_value,a_value,w_value,str(ts))
                                # store the data for TMS status broadcast
                                self.position_dec_status = x_value+" "+y_value+" "+a_value+" "+w_value
                                self.__configApi.update(
                                    tmsconfig.UNO_ID,
                                    teks_db_configure.UNO_TOP_MODULE_STATS_TYPE[teks_db_configure.UNO_POSITION_INDEX].replace(" ", "_"),
                                    data={_CONFIG_COMD:self.position_dec_status,_CONFIG_T:"a"}
                                    )
                                self.position_status = " ".join(results)
                                self.__configApi.update(
                                    tmsconfig.UNO_ID,
                                    teks_db_configure.UNO_TOP_MODULE_STATS_TYPE[teks_db_configure.UNO_POSITION_HEX_INDEX].replace(" ", "_"),
                                    data={_CONFIG_COMD:self.position_status,_CONFIG_T:"a"}
                                    )
                                # self.logger.debug("navi status results: "+str(self.position_status)+" "+self.out_msg)
                                if self.onPositionChangeFunction:
                                    self.onPositionChangeFunction()
                            else:
                                pass

                        elif isBatteryStatus:
                            self.logger.debug("isBatteryStatus")
                            self.battery_status = str(isBatteryStatus)
                            self.logger.debug("battery status: "+str(self.battery_status)+" {:%Y%m%d}".format(datetime.now())+" "+self.out_msg)

                            self.__configApi.update(
                                tmsconfig.UNO_ID,
                                teks_db_configure.UNO_TOP_MODULE_STATS_TYPE[teks_db_configure.UNO_BATTERY_LEVEL_INDEX].replace(" ", "_"),
                                data={_CONFIG_COMD:str(self.battery_status),_CONFIG_T:"a"}
                                )
                            if self.onBatteryChangeFunction:
                               self.onBatteryChangeFunction()

                        elif isSwitchMapSuccessStatus:
                            self.logger.debug("isSwitchMapSuccessStatus")
                            self.switch_map_success_status = isSwitchMapSuccessStatus
                            if self.onSwitchMapSuccessFunction:
                               self.onSwitchMapSuccessFunction()

                        elif isObstacle:
                            self.logger.debug("isObstacle")
                        else:
                            if self.position_counter > 0:
                                # self.logger.debug("call get location in navi status")
                                if (self.position_counter/5) == 0:
                                    results = uno_cmd.getLocation(self.__ser_port)
                                # if results and len(results) > 0:
                                #     #store results into database based on mapid and routeid
                                #     ts = ""+str(self.dbapi.gen_timestamp())
                                #     x_value = str(utils.get_corrd_in_dec(results[0]))
                                #     y_value = str(utils.get_corrd_in_dec(results[1]))
                                #     a_value = str(utils.get_corrd_in_dec(results[2]))
                                #     w_value = str(utils.get_corrd_in_dec(results[3]))

                                #     self.ui_db.set_top_module_location(x_value,y_value,a_value,w_value,str(ts))
                                #     # store the data for TMS status broadcast
                                #     self.__configApi.update(
                                #         tmsconfig.UNO_ID,
                                #         config_name=teks_db_configure.UNO_TOP_MODULE_STATS_TYPE[teks_db_configure.UNO_POSITION_INDEX].replace(" ", "_"),
                                #         data={_CONFIG_COMD:x_value+" "+y_value+" "+a_value+" "+w_value,_CONFIG_T:"a"}
                                #         )
                                #     self.position_status = " ".join(results)
                                #     self.__configApi.update(
                                #         tmsconfig.UNO_ID,
                                #         teks_db_configure.UNO_TOP_MODULE_STATS_TYPE[teks_db_configure.UNO_POSITION_HEX_INDEX].replace(" ", "_"),
                                #         data={_CONFIG_COMD:self.position_status,_CONFIG_T:"a"}
                                #         )
                                #     if self.onPositionChangeFunction:
                                #         self.onPositionChangeFunction()
                                #     # self.logger.debug("position sresults: "+str(results))
                                # # self.position_counter = tmsconfig.INTERVAL_COLLECTSTATUS
                            else:
                                # self.battery_status = uno_cmd.getBatteryStatus(self.__ser_port)
                                # if self.battery_status is None:
                                #     self.battery_status = "N/A"
                                # self.__configApi.update(
                                #     tmsconfig.UNO_ID,
                                #     config_name=teks_db_configure.UNO_TOP_MODULE_STATS_TYPE[teks_db_configure.UNO_BATTERY_LEVEL_INDEX].replace(" ", "_"),
                                #     data={_CONFIG_COMD:self.battery_status,_CONFIG_T:"a"}
                                #     )
                                # if self.onBatteryChangeFunction:
                                #    self.onBatteryChangeFunction()
                                self.position_counter = tmsconfig.INTERVAL_COLLECTBATTERYSTATUS
                                pass

                            self.position_counter -= 1
                            pass
        else:
            self.__status = "03"
            time.sleep(10.0)
            # ts = ""+str(utils.gen_timestamp())
            ts = utils.now_string()
            self.__configApi.update(
                tmsconfig.UNO_ID,
                config_name=teks_db_configure.UNO_TOP_MODULE_STATS_TYPE[teks_db_configure.UNO_NAVI_STATUS_INDEX].replace(" ", "_"),
                data={_CONFIG_COMD:self.__status,_CONFIG_T:"a"}
                )
            self.__configApi.update(
                tmsconfig.UNO_ID,
                config_name=teks_db_configure.UNO_TOP_MODULE_STATS_TYPE[teks_db_configure.UNO_POSITION_INDEX].replace(" ", "_"),
                data={_CONFIG_COMD:"100 200 300 400",_CONFIG_T:"a"}
                )
            self.__configApi.update(
                tmsconfig.UNO_ID,
                config_name=teks_db_configure.UNO_TOP_MODULE_STATS_TYPE[teks_db_configure.UNO_BATTERY_LEVEL_INDEX].replace(" ", "_"),
                data={_CONFIG_COMD:"88",_CONFIG_T:"a"}
                )
            if self.onChangeFunction:
                self.onChangeFunction()

        self.start()
        pass

    @property
    def is_suspend(self):
        return self.__suspend_flag

    # def start(self):
    #     self.start()

