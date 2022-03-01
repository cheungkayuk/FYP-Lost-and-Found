import torch

MODEL = "yolov5s"

FILTER = ["suitcase", "cell phone", "backpack", "handbag"]

class Detecter:
    def __init__(self, model = MODEL):
        try:
            # Model
            self.model = torch.hub.load('ultralytics/yolov5', model)  # or yolov5m, yolov5l, yolov5x, etc.
        except:
            print("Error in Detecter: fail to load model")

    #return list of records
    def scanImg(self, imgpath, showImg = False, filter = True, showResult = False, saveFile = False, savePath = "Results_IMG"):

        results = self.model(imgpath)
        txt_results = results.pandas().xyxy[0]

        if showImg:
            results.show()
        
        if showResult:
            #      xmin    ymin    xmax   ymax  confidence  class    name
            print(txt_results)

        if saveFile:
            results.save(savePath)

        objectlist = txt_results.to_dict(orient='records')

        if filter:
            for obj in reversed(objectlist):
                if not (obj["name"] in FILTER):
                    objectlist.remove(obj)


        return objectlist

# Sample

# detecter = Detecter()

# detecter.scanImg("example1.jpg", showImg=True, showResult=True)
