import torch
import cv2
import os
from datetime import datetime

MODEL = "yolov5s"

FILTER = ["suitcase", "cell phone", "backpack", "handbag", "bed"]

class Detector:
    def __init__(self, model = MODEL):
        try:
            # Model
            self.model = torch.hub.load('ultralytics/yolov5', model)  # or yolov5m, yolov5l, yolov5x, etc.
        except:
            print("Error in Detecter: fail to load model")

    #return list of records
    def scanImg(self,
                img_path,
                showImg = False,
                filter = True,
                showResult = False,
                saveImg = False,
                saveCrop = False,
                savePath = "Results"):

        results = self.model(img_path)
        txt_results = results.pandas().xyxy[0]

        if showImg:
            results.show()
        
        if showResult:
            #      xmin    ymin    xmax   ymax  confidence  class    name
            print(txt_results)

        if saveImg:
            saveDir = savePath + "/Images"
            results.save(saveDir)

        objectlist = txt_results.to_dict(orient='records')

        if filter:
            for obj in reversed(objectlist):
                if not (obj["name"] in FILTER):
                    objectlist.remove(obj)

        id = 1
        for obj in reversed(objectlist):
            now = datetime.now()
            current_time = now.strftime("%Y%m%d_%H%M%S")

            obj["id"] = current_time + '_' + str(id)
            id+=1

        if saveCrop:
            img = cv2.imread(img_path)
            saveDir = savePath + "/Crops"
            if not os.path.exists(saveDir):
                os.makedirs(saveDir)
   
            for obj in reversed(objectlist):
                xmin = int(obj.get('xmin'))
                ymin = int(obj.get('ymin'))
                xmax = int(obj.get('xmax'))
                ymax = int(obj.get('ymax'))
                crop_img = img[ymin:ymax, xmin:xmax]
                filename = obj["id"] + '.jpg'
                filepath =  os.path.join(saveDir, filename)
                cv2.imwrite(filepath, crop_img)
    

        return objectlist

# Sample

# detector = Detector()

# print(detector.scanImg("example1.jpg", showImg=True, showResult=False, saveCrop=True))
