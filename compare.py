# from Detector.Detector import Detector
# from MongoController.MongoController import MongoController
from Similarity.Similarity import Similarity
# from Telegram_Manager.Alerter import Alerter

import time

TIME_THRESHOLD_SECOND = 1
IOU_2_SCENE = 0.6
IOU_1_SCENE = 0.85

s = Similarity()

def iou_cal(box1, box2):
    # box:[x1,y2,x2,y2]-->[xmin, ymin, xmax, ymax]
    area_box1 = ((box1["xmax"] - box1["xmin"] + 1) * (box1["ymax"] - box1["ymin"] + 1))
    area_box2 = ((box2["xmax"] - box2["xmin"] + 1) * (box2["ymax"] - box2["ymin"] + 1))
    inter_h = max(0, min(box1["xmax"], box2["xmax"]) - max(box1["xmin"], box2["xmin"]) + 1)
    inter_w = max(0, min(box1["ymax"], box2["ymax"]) - max(box1["ymin"], box2["ymin"]) + 1)
    inter = inter_w * inter_h
    union = area_box1 + area_box2 - inter
    iou = inter / union
    return iou

def compare2scene(scene1, scene2, sim_method = "all"):
    newlist = [0] * len(scene2)

    report_list = []
    
    for scene1obj in reversed(scene1):
        match = False
        for i,scene2obj in enumerate(scene2):

            if (scene1obj["name"] == scene2obj["name"]):
                iou = iou_cal(scene1obj, scene2obj)
                # print("\n")
                # print(scene1obj["name"], scene2obj["name"])
                # print(iou)
                # print("\n")

                if (iou > IOU_2_SCENE):
                    r = s.similarity(scene1obj["img_path"],scene2obj["img_path"], method=sim_method)
                    if r[0]:    #similarity(pic1,pic2)>0.5
                        match = True
                        newlist[i] += 1
                        timed = (scene2obj["time"] - scene1obj["time"])
                        timed = timed.total_seconds()
                        if timed > TIME_THRESHOLD_SECOND:   #time being placed for long time
                            pass
                            #report
                            report_list.append(scene1obj)
                            scene1.remove(scene1obj)
                        else:   #Two objects are the same one but not exceeds the threshold yet
                            pass
                        break

        if match == False:
            print(scene1obj["name"], "is disappear!\n")
            scene1.remove(scene1obj) #delete from database
            

    # print(newlist)
    for i in range(len(newlist)):
        if newlist[i] == 0:
            print(scene2[i]["name"], " Is new!!\n")
            scene1.append(scene2[i]) #add to database

    return report_list

def findstationaryobj(scene1, scene2, sim_method = "all"):
    for scene1obj in reversed(scene1):
        match = False
        for i,scene2obj in enumerate(scene2):

            if (scene1obj["name"] == scene2obj["name"]):
                iou = iou_cal(scene1obj, scene2obj)


                if (iou > IOU_1_SCENE):
                    r = s.similarity(scene1obj["img_path"],scene2obj["img_path"], method=sim_method)
                    if r[0]:    #similarity(pic1,pic2)>0.5
                        match = True
                        break

        if match == False:
            scene1.remove(scene1obj)

    return


#sample

# detecter = Detector()
# alerter = Alerter()

# controller = MongoController()

# oblist1 = controller.queryFromDbDirectionName("A", "A0")

# obj = oblist1[0]

# alerter.sendToLog(obj["full_img"], obj["name"], "A1", "gg", obj["time"])
# alerter.readAndSendFromLog()

#///////////////////////////////////////////////////////////////////

# sendToLog(self, imgFileName, className, checkpoint, direction, detectedTime)

# oblist2 = detecter.scanImg("img1.jpg", filter=False, saveCrop=True, showResult=False, saveImg=True)

# controller.updateData("A", "A0", oblist2)

# time.sleep(5)

# oblist3 = detecter.scanImg("img3.jpg", filter=False, saveCrop=True, showResult=False)

# result = compare2scene(oblist2, oblist3)

# controller.updateData("A", "A0", oblist2)

# print("\n\nReport item:")
# for item in result:
#     print(item["name"])
# print(result)




