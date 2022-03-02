import serial
import struct
import math

# b'Uw\x03\x02\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00'

# getlocation: 
# 55770201000000000000000000000000000000000000000000000000
# b'Uw\x02\x01\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00'

SERIAL_PORT = "COM10"
SERIAL_BAUD = 115200

GET_LOCATION = b'Uw\x02\x01\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00'

def getlocation(ser):
    ser.write(GET_LOCATION)
    print("Get location...")
    serBarCode = ser.read(30)
    print(f"received: {serBarCode.hex()}")
    x = serBarCode[4:8]
    y = serBarCode[8:12]
    a = serBarCode[12:16]
    w = serBarCode[16:20]
    
    x = struct.unpack('<f', x)[0]
    y = struct.unpack('<f', y)[0]
    a = struct.unpack('<f', a)[0]
    w = struct.unpack('<f', w)[0]
    
    th = -math.atan2(2*a*w,w*w-a*a)
    th = th*180/math.pi
    return [x,y,a,w,th]

def main():
    ser = serial.Serial(SERIAL_PORT, SERIAL_BAUD, timeout=5)

    # print("get location...")
    # serBarCode = ser.read(30)
    # # ser.write(b'Uw\x03\x02\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00')
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

    print(getlocation(ser))
    ser.close()

main()

