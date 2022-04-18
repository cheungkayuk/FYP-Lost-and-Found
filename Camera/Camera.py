from hikvisionapi import Client
from PIL import Image
from io import BytesIO

# http://192.168.8.111/ISAPI/Streaming/channels/101/picture

IP = "http://192.168.8.111"
USERNAME = "admin"
PW = "fyp202020"


class Camera:
    def __init__(self, ip = IP, username = USERNAME, pw = PW):
        try:
            self.cam = Client(ip, username, pw)
        except:
            print("Error in Camera: fail to connect the camera")

    # get the current frame captured by the camera
    def getimg(self):
        img =  self.cam.Streaming.channels[101].picture(method='get', type='opaque_data')
        return Image.open(BytesIO(img.content))

# camera = Camera()
# img = camera.getimg()
# img.show()

#response = requests.get("http://admin:fyp202020@192.168.8.111/ISAPI/Streaming/channels/101/picture")
