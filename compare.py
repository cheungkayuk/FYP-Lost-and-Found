from Detector.Detector import Detector
import time

TIME_THRESHOLD_SECOND = 1

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

def compare2scene(scene1, scene2):
    newlist = [0] * len(scene2)
    
    for scene1obj in scene1:
        match = False
        for i,scene2obj in enumerate(scene2):

            if (scene1obj["name"] == scene2obj["name"]):
                iou = iou_cal(scene1obj, scene2obj)
                print("\n")
                print(scene1obj["name"], scene2obj["name"])
                print(iou)
                print("\n")

                if (iou > 0.5):
                    if True:    #similarity(pic1,pic2)>0.5
                        match = True
                        newlist[i] += 1
                        timed = (scene2obj["timestamp"] - scene1obj["timestamp"])
                        timed = timed.total_seconds()
                        if timed > TIME_THRESHOLD_SECOND:   #time being placed for long time
                            pass
                            #report
                        else:   #Two objects are the same one but not exceeds the threshold yet
                            pass
                        break

        if match == False:
            print(scene1obj, "is disappear!\n") #delete from database

    print(newlist)
    for i in range(len(newlist)):
        if newlist[i] == 0:
            print(scene2[i], " Is new!!\n") #add to database



#sample

# detecter = Detector()

# oblist1 = detecter.scanImg("example1.jpg", filter=False, saveCrop=False, showResult=True)

# time.sleep(5)

# oblist2 = detecter.scanImg("example2.jpg", filter=False, saveCrop=False, showResult=True)

# compare2scene(oblist1, oblist2)



