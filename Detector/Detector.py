import imghdr
from numpy import source
from numpy import asarray
import torch
import cv2
import os
from datetime import datetime

# our selected pretrained model
MODEL = "yolov5s"

# 1st class objects
# Since YOLOv5s does not include wallet, 'wallet' is not included in FILTER1
FILTER1 = ["cell phone"]

# 2nd class objects
FILTER2 = ["suitcase", "backpack", "handbag"]

# Claas Detector
class Detector:
    # Initialise the model (load the model weights)
    # Assign Director.id = 1 for saving images
    # Parameter: model: the object detection model
    def __init__(self, model = MODEL):
        self.working = False
        try:
            # Model
            self.model = torch.hub.load('ultralytics_yolov5_master', "custom", path="yolov5s.pt", source="local" )  # or yolov5m, yolov5l, yolov5x, etc.
        except:
            print("Error in Detecter: fail to load model")
        Detector.id = 1

    # Perform object detection in an image
    # Input:
    #     img_path: image path for object detection
    #     showImg: whether to show the result image, default = False,
    #     filter: whether to filter the classes, default = True,
    #     mode: which mode the robot is running, mode = 1: filter 1st class objects, mode = 2: filter 2nd class objects,
    #                                            default = 2,
    #     showResult: whether to show the result (list of detected objects), default = False,
    #     saveImg: wheather to save images, filename contains the current time, default = True,
    #     saveCrop whether to save crops, filename contains the current time_Director.id,
    #                                     default = True,
    #     savePath: the directory path for saving, default = "Results"
    # Output: return list of records containing the following information of each detected object
    #           {'class', 'confidence', 'img_path', 'name', 'obj_id', 'time', 'xmax', 'xmin', 'ymax', 'ymin' (bounding box)}
    def scanImg(self,
                img_path,
                showImg = False,
                filter = True,
                mode = 2,
                showResult = False,
                saveImg = True,
                saveCrop = True,
                savePath = "Results"):

        self.working = True
        
        results = self.model(img_path)
        txt_results = results.pandas().xyxy[0]

        if showImg:
            results.show()

        objectlist = txt_results.to_dict(orient='records')

        if filter:
            if (mode == 1):
                FILTER = FILTER1
            else:
                FILTER = FILTER2
            for obj in reversed(objectlist):
                if not (obj["name"] in FILTER):
                    objectlist.remove(obj)

        now = datetime.now()
        current_time = now.strftime("%Y%m%d_%H%M%S")
        saveDir = savePath + "/Images/" + current_time + "/"
        fileName = current_time + ".jpg"
        if saveImg:
            results.save(save_dir=saveDir)
            oldname = os.listdir(saveDir)[0]
            os.rename(saveDir + oldname, saveDir + fileName)

        for obj in objectlist:

            obj["obj_id"] = current_time + '_' + str(Detector.id)
            obj["time"] = now
            obj["img_path"] = savePath + "/Crops/" + obj["obj_id"] + ".jpg"
            obj["full_img"] = saveDir + fileName
            Detector.id+=1

        if saveCrop:
            # img = cv2.imread(saveDir + fileName)
            img = asarray(img_path)
            # print(type(img))
            saveDir = savePath + "/Crops"
            if not os.path.exists(saveDir):
                os.makedirs(saveDir)
   
            for obj in objectlist:
                xmin = int(obj.get('xmin'))
                ymin = int(obj.get('ymin'))
                xmax = int(obj.get('xmax'))
                ymax = int(obj.get('ymax'))
                crop_img = img[ymin:ymax, xmin:xmax]
                filename = obj["obj_id"] + ".jpg"
                filepath =  os.path.join(saveDir, filename)
                cv2.imwrite(filepath, crop_img)
    
        if showResult:
            print(objectlist)

        self.working = False
        return objectlist

# Sample

# detector = Detector()

# detector.scanImg("example5.jpg", showImg=True, saveCrop=False, showResult=True)
