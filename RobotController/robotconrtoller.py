import serial
import struct
import math
import time

# b'Uw\x03\x02\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00'

# getlocation: 
# 55770201000000000000000000000000000000000000000000000000
# b'Uw\x02\x01\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00'

# goto:
# 55770102(x)(y)(a)(w)0000000000000000
# return_goto:
# 55770303(status)00000000000000000000000000000000000000000000000000

SERIAL_PORT = "COM10"
SERIAL_BAUD = 115200

GET_LOCATION = b'Uw\x02\x01\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00'

Point_A = (1.446,7.002,0,1)
Point_B = (3.814,6.426,0,1)
Point_C = (6.541,5.683,0,1)

#///////////////////////////////////////////////////////////////////////////////////

def hextodec(hexinput):
    return struct.unpack('<f', bytes.fromhex(hexinput))[0]
    # print(query)
    # return(struct.unpack('<f', query))

def dectohex(decinput):
    hexnumber = ( hex(struct.unpack('<I', struct.pack('>f',decinput))[0]) )
    hexstring = str(hexnumber)[2::]
    if (len(hexstring) < 8):
        hexstring = "00000000"[0:8-len(hexstring)] + hexstring
    return (hexstring)

def bytetodec(byteinput):
    return (struct.unpack('<f', byteinput))

def dectobyte(decinput):
    hexinput = dectohex(decinput)
    return bytes.fromhex(hexinput)

#///////////////////////////////////////////////////////////////////////////////////

class Robot_Controller:
    def __init__(self):
        self.ser = serial.Serial(SERIAL_PORT, SERIAL_BAUD, timeout=5)
        self.moving = False

    def getlocation(self):
        self.ser.write(GET_LOCATION)
        print("Get location...")
        serBarCode = ser.read(30)
        print(f"received: {serBarCode.hex()}")
        x = serBarCode[4:8]
        y = serBarCode[8:12]
        a = serBarCode[12:16]
        w = serBarCode[16:20]

        print(type(serBarCode.hex()))
        
        x = struct.unpack('<f', x)[0]
        y = struct.unpack('<f', y)[0]
        a = struct.unpack('<f', a)[0]
        w = struct.unpack('<f', w)[0]
        
        th = -math.atan2(2*a*w,w*w-a*a)
        th = th*180/math.pi
        return [x,y,a,w,th]

    def goto(self, point):
        self.moving = True

        command = "55770102"
        command += dectohex(point[0])
        command += dectohex(point[1])
        command += dectohex(point[2])
        command += dectohex(point[3])
        command += "0000000000000000"
        command = bytes.fromhex(command)

        self.ser.write(command)
        print("Sent GoTo Command...")
        while True:
            serBarCode = self.ser.read(30)
            if (serBarCode.hex()[0:10] == "5577030303"):
                print(f"received: {serBarCode.hex()}")
                print("reach point successfully.\n")
                self.moving = False
                return True

    def close(self):
        self.ser.close()
    #///////////////////////////////////////////////////////////////////////////////////
    #///////////////////////////////////////////////////////////////////////////////////

# print("get location...")
# serBarCode = ser.read(30)
# ser.write(b'Uw\x03\x02\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00')
# print(serBarCode)
# print("\n")
# hexdata = serBarCode.hex()
# print(hexdata)
# print("\n")
# bytedata = bytes.fromhex(hexdata)
# print(bytedata)
# print("\n")
# print(serBarCode == bytedata)
# print("\n\n")



# main()
# goto(Point_A)
# print(dectohex(Point_A[3]))


# getlocation()
# goto(Point_A)








