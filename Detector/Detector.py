import torch
import cv2
import os
from datetime import datetime

MODEL = "yolov5l"

FILTER = ["suitcase", "cell phone", "backpack", "handbag"]

class Detector:
    def __init__(self, model = MODEL):
        try:
            # Model
            self.model = torch.hub.load('ultralytics/yolov5', model)  # or yolov5m, yolov5l, yolov5x, etc.
        except:
            print("Error in Detecter: fail to load model")
        Detector.id = 1

    #return list of records
    def scanImg(self,
                img_path,
                showImg = False,
                filter = True,
                showResult = False,
                saveImg = True,
                saveCrop = True,
                savePath = "Results"):

        results = self.model(img_path)
        txt_results = results.pandas().xyxy[0]

        if showImg:
            results.show()

        objectlist = txt_results.to_dict(orient='records')

        if filter:
            for obj in reversed(objectlist):
                if not (obj["name"] in FILTER):
                    objectlist.remove(obj)

        for obj in objectlist:
            now = datetime.now()
            current_time = now.strftime("%Y%m%d_%H%M%S")

            obj["obj_id"] = current_time + '_' + str(Detector.id)
            obj["time"] = now
            obj["img_path"] = obj["obj_id"] + ".jpg"
            Detector.id+=1

        if saveImg:
            saveDir = savePath + "/Images/" + current_time + "/"
            fileName = current_time + ".jpg"
            results.save(saveDir)
            oldname = os.listdir(saveDir)[0]
            os.rename(saveDir + oldname, saveDir + fileName)

        if saveCrop:
            img = cv2.imread(img_path)
            saveDir = savePath + "/Crops"
            if not os.path.exists(saveDir):
                os.makedirs(saveDir)
   
            for obj in objectlist:
                xmin = int(obj.get('xmin'))
                ymin = int(obj.get('ymin'))
                xmax = int(obj.get('xmax'))
                ymax = int(obj.get('ymax'))
                crop_img = img[ymin:ymax, xmin:xmax]
                filename = obj["img_path"]
                filepath =  os.path.join(saveDir, filename)
                cv2.imwrite(filepath, crop_img)
    
        if showResult:
            print(objectlist)

        return objectlist

# Sample

# detector = Detector()

# detector.scanImg("example5.jpg", showImg=True, saveCrop=False, showResult=True)
