from src.MongoController import MongoController
import time

checkpointName = "B"
checkpointX = 10
checkpointY = 12


data = {
    "directions" : [
        {
            "direction": 250,
            "detectedObjects": [
                {
                    "className" : 'handbag',
                    "xmin": 459,
                    "ymin": 802,
                    "xmax": 1161,
                    "ymax": 1720,
                    "time": time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
                },
                {
                    "className" : 'cellphone',
                    "xmin": 12,
                    "ymin": 10,
                    "xmax": 100,
                    "ymax": 1000,
                    "time": time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
                },
                {
                    "className" : 'suitcase',
                    "xmin": 1459,
                    "ymin": 1802,
                    "xmax": 1061,
                    "ymax": 720,
                    "time": time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
                }
            ]
        },
        {
            "direction": -110,
            "detectedObjects": [
                {
                    "className" : 'cellphone',
                    "xmin": 49,
                    "ymin": 80,
                    "xmax": 116,
                    "ymax": 170,
                    "time": time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
                },
                {
                    "className" : 'cellphone',
                    "xmin": 112,
                    "ymin": 110,
                    "xmax": 1100,
                    "ymax": 100,
                    "time": time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
                },
                {
                    "className" : 'purse',
                    "xmin": 159,
                    "ymin": 182,
                    "xmax": 101,
                    "ymax": 70,
                    "time": time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
                }
            ]
        }
    ] 
}

newdetecedObjects = [
                {
                    'id': 1,
                    "className" : 'suitcase',
                    "xmin": 149,
                    "ymin": 180,
                    "xmax": 176,
                    "ymax": 1170,
                    "imgsrc": '/img/C/C1/01.jpg',
                    "time": time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
                },
                {
                    'id': 2,
                    "className" : 'purse',
                    "xmin": 1149,
                    "ymin": 1180,
                    "xmax": 1116,
                    "ymax": 1170,
                    "imgsrc": '/img/C/C1/02.jpg',
                    "time": time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
                },
                {
                    'id': 3,
                    "className" : 'purse',
                    "xmin": 4911,
                    "ymin": 801,
                    "xmax": 1161,
                    "ymax": 1701,
                    "imgsrc": '/img/C/C1/03.jpg',
                    "time": time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
                }
            ]



controller = MongoController()
# pass in checkpoint coordinate, then direction angle
controller.createNewCheckpoint("C", 100, 100, [120, -120, 360])
controller.updateData("C", "C1", newdetecedObjects)
controller.queryFromDbDirectionName("C", "C1")
#controller.deleteData("C", "C1", 1, "suitcase")
#controller.queryFromDbDirectionName("C", "C1")
