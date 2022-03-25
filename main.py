from Detector.Detector import Detector
from MongoController.MongoController import MongoController
from RobotController.robotconrtoller import Robot_Controller
from compare import *
import threading
import asyncio
import time
from time import sleep

###################################################################################
A0 = ["A1",(3.558732032775879, 6.074324131011963, 0.977596640586853, 0.21048696339130402)]
A1 = ["A0",(3.558732032775879, 6.074324131011963, -0.7992277145385742, 0.6010283827781677)]
B0 = ["B0",(6.456136703491211, 5.444826602935791, -0.08248760551214218, 0.996592104434967)]
B1 = ["B1",(6.456136703491211, 5.444826602935791, -0.8250911235809326, 0.5649996995925903)]
# B0 = ["B1",(11.809239387512207, 4.119314670562744, -0.13229386508464813, 0.9912105202674866)]
# B1 = ["B2",(11.817338943481445, 4.065883159637451, -0.777592658996582, 0.6287683248519897)]
# Point_B = (3.814,6.426,0,1)
# Point_C = (6.541,5.683,0,1)

CAMERA_IP = ""
CAMERA_USER = ""
CAMERA_PW = ""
CAMERA_PIC = ""

PATROL_PATH = [A0, A1, B0, B1]
###################################################################################


class LAF_Robot():
    def __init__(self, start_idx=0, enable_t = True):
        self.detector = Detector()
        self.dbcontroller = MongoController()
        self.robotcontroller = Robot_Controller()

        self.patrol_path = PATROL_PATH
        self.current_idx = start_idx
        self._scan_road = 0

        self.mode = 0   # 0: nothing    1: 1st class    2: 2nd class
        self.t = threading.Thread(target=self._scan_road)
        self.enable_t = enable_t

        self.keep_patrol = True

        # connect to camera
        # self.cam = Client(f"http://{CAMERA_IP}", CAMERA_USER, CAMERA_PW)

    def start_patrol(self):
        while(self.keep_patrol):
            target_idx = (self.current_idx + 1)%len(self.patrol_path)
            target_point = self.patrol_path[target_idx]

            self.mode = 1
            goto_success = self.robotcontroller.goto(target_point[1])
            if goto_success:
                self.current_idx = target_idx
                self.mode = 2
                pt = self.cur_pt()

                oblist1 = self.controller.queryFromDbDirectionName("A", "A0")

                ##############################################
                oblist2 = self.detecter.scanImg(CAMERA_PIC)
                sleep(2)
                oblist3 = self.detecter.scanImg(CAMERA_PIC)
                ##############################################

                findstationaryobj(oblist2, oblist3)
                
                report_list = compare2scene(oblist1, oblist2)

                if len(report_list):    #not empty
                    #report
                    pass

                self.controller.updateData(pt[0][0],pt[0], oblist1)

                # SCAN CHECKPOINT
            else:
                sleep(5)
                continue
        
    def t_scan_road(self):
        print("_scan_road started\n")
        new_loop = asyncio.new_event_loop()
        asyncio.set_event_loop(new_loop)
        loop = asyncio.get_event_loop()

        while self.enable_t: 
            if (self.robotcontroller.moving) and (self.mode == 1):
                # SCAN ROAD
                sleep(0.1)
            
            else:
                sleep(0.1)
                continue

    def t_start_scan_road(self):
        self.t.start()
        
    def t_kill_t(self):
        self.enable_t = False

    def cur_pt(self):
        return self.patrol_path(self.current_idx)

    def get_img(self):
        pass

    def init_database(self):
        self.controller.createNewCheckpoint("A", 1.446, 7.002, [(0,1)])

robot = LAF_Robot()

robot.robotcontroller.goto(A0[1])
robot.robotcontroller.goto(A1[1])
robot.robotcontroller.goto(B0[1])
robot.robotcontroller.goto(B1[1])
