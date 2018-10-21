import serial
import time

def int2hex(number, bits):
    if number < 0:
        h = hex((1 << bits) + number)
        return ('0x' + h[2:].zfill(4))
    else:
        h = hex(number)
        return ('0x' + h[2:].zfill(4))

def init():
    return serial.Serial(port='/dev/serial0', baudrate=115200)
    time.sleep(1)

ser = init()

def start():
    ser.write(chr(128))
    time.sleep(1)
    ser.write(chr(131))

def drive(velocity, radius):
    operand = '89'
    vel_hex = int2hex(velocity, 16)
    vel_high = str(vel_hex[2:4])
    vel_low = vel_hex[4:6]
    rad_hex = int2hex(radius, 16)
    rad_high = rad_hex[2:4]
    rad_low = rad_hex[4:6]
    s = str(operand + vel_high + vel_low + rad_high + rad_low)
    print('Drive cmd: ' + s)
    ser.write(s.decode('hex'))

def rotate_left(velocity):
    operand = '91'
    right_hex = int2hex(velocity, 16)
    right_high = str(right_hex[2:4])
    right_low = right_hex[4:6]
    left_hex = int2hex(-velocity, 16)
    left_high = left_hex[2:4]
    left_low = left_hex[4:6]
    s = str(operand + right_high + right_low + left_high + left_low)
    print('Drive cmd: ' + s)
    ser.write(s.decode('hex'))

SPEED = 50
TURN_VEL = 100
TURN_RAD = 50

def move(forward, left, right):
    if not forward and not left and not right: #stand still
        drive(0,0)
    elif forward and not left and not right: #straight
        drive(SPEED, 0)
    elif forward and left and not right: #drive left
        drive(SPEED, TURN_RAD)
    elif forward and not left and  right: #drive right
        drive(SPEED, -TURN_RAD)
    elif not forward and left and not right: #rotate left
        rotate_left(TURN_VEL)
    elif not forward and not left and  right: #rotate right
        rotate_left(-TURN_VEL)
    else:
        print("YOU SHOULD NOT BE HERE")
        exit(1)


###############################
# MAIN
###############################

print("Start")
start()

import rospy
from std_msgs.msg import Int8

def callback(data):
    print("Got message")
    if data == 1:
        forward = True
        left = False
        right = False
    elif data == 2:
        forward = True
        left = True
        right = False
    elif data == 3:
        forward = True
        left = False
        right = True
    elif data == 4:
        forward = False
        left = True
        right = False
    elif data == 5:
        forward = False
        left = False
        right = True
    elif data == 6:
        forward = False
        left = False
        right = False
    # MOVE
    move(forward, left, right)


def listener():
    # run simultaneously.
    rospy.init_node('control_roomba', anonymous=True)

    rospy.Subscriber("pet_roomba3000", Int8, callback)

    # spin() simply keeps python from exiting until this node is stopped
    rospy.spin()


#########
# MAIN
#########

listener()
