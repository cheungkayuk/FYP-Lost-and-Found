from src.MongoController import MongoController
import time

checkpointName = "B"
checkpointX = 10
checkpointY = 12


data = {
    "directions" : [
        {
            "direction": 250,
            "detecedObjects": [
                {
                    "className" : 'handbag',
                    "boxCoordinates": {"topLeft": { "x": (123), "y": (456)} , "bottomRight": { "x": (567), "y": (890)} }
                },
                {
                    "className" : 'cellphone',
                    "boxCoordinates": {"topLeft": { "x": (3), "y": (46)} , "bottomRight": { "x": (57), "y": (0)} }
                },
                {
                    "className" : 'suitcase',
                    "boxCoordinates": {"topLeft": { "x": (23), "y": (56)} , "bottomRight": { "x": (56), "y": (89)} }
                }
            ]
        },
        {
            "direction": -110,
            "detecedObjects": [
                {
                    "className" : 'bag',
                    "boxCoordinates": {"topLeft": { "x": (123), "y": (456)} , "bottomRight": { "x": (567), "y": (890)} }
                },
                {
                    "className" : 'suitcase',
                    "boxCoordinates": {"topLeft": { "x": (3), "y": (46)} , "bottomRight": { "x": (57), "y": (0)} }
                },
                {
                    "className" : 'purse',
                    "boxCoordinates": {"topLeft": { "x": (23), "y": (56)} , "bottomRight": { "x": (56), "y": (89)} }
                }
            ]
        }
    ] 
}

newdetecedObjects = [
                {
                    "className" : 'purse',
                    "boxCoordinates": {"topLeft": { "x": (1123), "y": (1456)} , "bottomRight": { "x": (1567), "y": (1890)} }
                },
                {
                    "className" : 'purse',
                    "boxCoordinates": {"topLeft": { "x": (13), "y": (146)} , "bottomRight": { "x": (157), "y": (10)} }
                },
                {
                    "className" : 'purse',
                    "boxCoordinates": {"topLeft": { "x": (123), "y": (156)} , "bottomRight": { "x": (156), "y": (189)} }
                }
            ]



controller = MongoController()
controller.createNewCheckpoint("C", 100, 100, [120, -120, 360])
controller.updateData("C", "C1", newdetecedObjects, time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()))