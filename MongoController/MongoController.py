from pymongo import MongoClient
import time


class MongoController():

    # setup connection to mongodb
    # for testing purpose with no db, pls comment out the below 3 lines of code as well self.db.xxx in line 29, 39 and 78
    cluster = 'mongodb://localhost:27017'
    client = MongoClient(cluster)
    db = client.sample
    
    # create a new checkpoint in the database with empty detecedObjects
    # parameters: checkpointName, checkpointX(int), checkpointX(int), directions in degree e.g[120, -150], 120 degree and -150 degree in list form
    def createNewCheckpoint(self, checkpointName, checkpointX, checkpointY, directions):
        newCheckpoint = {}
        newCheckpoint['checkpointName'] = checkpointName
        newCheckpoint['checkpointX'] = checkpointX
        newCheckpoint['checkpointY'] = checkpointY
        newCheckpoint['directions'] = []
        for i in range(len(directions)):
            directionItem = {}
            directionItem['direction'] = directions[i]
            directionItem['directionName'] = checkpointName+str(i)
            directionItem['detecedObjects'] = []
            newCheckpoint['directions'].append(directionItem)
        newCheckpoint['time'] = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
        # save new checkpoint to db
        self.db.data.insert_one(newCheckpoint)
        print("saved Data!")



    # query from db with criteria
    # e.g
#     query = { "checkpointName": "B"} for parameter criterias
#     for query checkpoint name 'B'
    def queryFromDb(self, criterias):
        print(self.db.data.find_one(criterias))




    # e.g sample item for the detectedObjects parameter
    
    # newdetecedObjects = [
    #             {
    #                 "className" : 'purse',
    #                 "boxCoordinates": {"topLeft": { "x": (1123), "y": (1456)} , "bottomRight": { "x": (1567), "y": (1890)} }
    #             },
    #             {
    #                 "className" : 'purse',
    #                 "boxCoordinates": {"topLeft": { "x": (13), "y": (146)} , "bottomRight": { "x": (157), "y": (10)} }
    #             },
    #             {
    #                 "className" : 'purse',
    #                 "boxCoordinates": {"topLeft": { "x": (123), "y": (156)} , "bottomRight": { "x": (156), "y": (189)} }
    #             }
    #         ]
    
    # update the detecedObjects inside database as well as the time stamp
    # updates the list of detecdObjects
    # param, checkpointname, directionName, detecedObjects list, timestamp
    def updateData(self, checkPointName, directionName, detectedObjects, time):
        # filter the desired checkpoint and directionName of the checkpoint
        filter = {
            'checkpointName': checkPointName,
            'directions.directionName': directionName
        }
        # values to be updated
        updateValue = {
            "$set": {
                "directions.$.detecedObjects": detectedObjects,
                "time": time
            }
        }
        # update to db
        self.db.data.update_one(filter, updateValue)

'''
Sample data to play with

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


'''

