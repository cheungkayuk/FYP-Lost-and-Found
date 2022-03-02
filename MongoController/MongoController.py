from pymongo import MongoClient
import time

# need this for pymongo
# python -m pip install pymongo[snappy,gssapi,srv,tls]

# Mongodb atlas
# email: felixhahn721@yahoo.com
# password: Hahafe721
# choose FYP project

class MongoController():

    # setup connection to mongodb
    # for testing purpose with no db, pls comment out the below 3 lines of code as well self.db.xxx in line 29, 39 and 78
    cluster = 'mongodb://localhost:27017'
    # cluster = 'mongodb+srv://admin:admin@cluster0.gdbdm.mongodb.net/sample?retryWrites=true&w=majority'
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
            directionItem['detectedObjects'] = []
            newCheckpoint['directions'].append(directionItem)
        newCheckpoint['time'] = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
        # save new checkpoint to db
        self.db.data.insert_one(newCheckpoint)
        print(f"Created checkpoint {checkpointName}!")



    # query from db with criteria
    # e.g
#     query = { "checkpointName": "B",
#               directions.direcname: B1} for parameter criterias
#     for query checkpoint name 'B'
    def queryFromDb(self, criterias):
        print(self.db.data.find_one(criterias))



    # query from database with directionname
    def queryFromDbDirectionName(self, checkpointName, directionName):
        result = self.db.data.find_one(
           {'directions': { '$elemMatch' : {'directionName': directionName} } }
        )

        if result == None:
            print("Not found")
        
        for i in result['directions']:
            if i['directionName'] == directionName:
                target = i['detectedObjects']
       
        print(target)
        return target


    # e.g sample item for the detectedObjects parameter
    
    # newdetecedObjects = [
    #             {
    #                 'id': 1,
    #                 "className" : 'suitcase',
    #                 "xmin": 149,
    #                 "ymin": 180,
    #                 "xmax": 176,
    #                 "ymax": 1170,
    #                 "imgsrc": '/img/C/C1/01.jpg',
    #                 "time": time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
    #             },
    #             {
    #                 'id': 2,
    #                 "className" : 'purse',
    #                 "xmin": 1149,
    #                 "ymin": 1180,
    #                 "xmax": 1116,
    #                 "ymax": 1170,
    #                 "imgsrc": '/img/C/C1/02.jpg',
    #                 "time": time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
    #             },
    #             {
    #                 'id': 3,
    #                 "className" : 'purse',
    #                 "xmin": 4911,
    #                 "ymin": 801,
    #                 "xmax": 1161,
    #                 "ymax": 1701,
    #                 "imgsrc": '/img/C/C1/03.jpg',
    #                 "time": time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
    #             }
    #         ]

    # update the detecedObjects inside database as well as the time stamp
    # updates the list of detecdObjects
    # param, checkpointname, directionName, detecedObjects list, timestamp
    def updateData(self, checkPointName, directionName, detectedObjects):
        # filter the desired checkpoint and directionName of the checkpoint
        filter = {
            'checkpointName': checkPointName,
            'directions.directionName': directionName
        }
        # values to be updated
        updateValue = {
            "$set": {
                "directions.$.detectedObjects": detectedObjects
            }
        }
        # update to db
        self.db.data.update_one(filter, updateValue)
        print(f"Updated data to checkpoint {checkPointName} direction {directionName}")
    
    #
    # delete data
    def deleteData(self, checkPointName, directionName, objectid, objectName):
        
        result = self.queryFromDbDirectionName(checkPointName, directionName)

        target = [i for i in result if not (i['id'] == objectid)]
        
        self.updateData(checkPointName, directionName, target)  
        print(f"Removed {objectName} with id {objectid} in checkpoint {checkPointName} direction {directionName}")     

