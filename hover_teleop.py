#!/usr/bin/env python3


import pigpio  # importing GPIO library
import rospy
import tty
import sys
import termios
import numpy as np
import keyboard
from std_msgs.msg import String
from geometry_msgs.msg import Twist
import os  # importing os library so as to communicate with the system
import time  # importing time library to make Rpi wait because its too impatient
from gpiozero import Servo
from time import sleep
from sensor_msgs.msg import LaserScan


# As i said it is too impatient and so if this delay is removed you will get an error
time.sleep(1)
global max_value
global min_value
global pub
global vel

x = 0
y = 0


pub = rospy.Publisher('cmd_vel', Twist, queue_size=10)


vel=input('Velocidad nominal:  ')
vel = int(vel)
max_value = 2000  # change this if your ESC's max value is different or leave it be
min_value = 700  # change this if your ESC's min value is different or leave it be

message = Twist()
message.linear.x = 0
message.linear.y = 0
message.linear.z = 0
message.angular.x = 0
message.angular.y = 0
message.angular.z = 0


def hover_teleop():

    rospy.init_node('hover_teleop', anonymous=True)

    print("For first time launch, select calibrate")
    print("Type the exact word for the function you want")
    print("calibrate OR control OR arm OR stop OR automat")

    pub.publish(message)

    inp = input()

    if inp == "calibrate":
        calibrate()
    elif inp == "arm":
        arm()
    elif inp == "control":
        control()
    elif inp == "stop":
        stop()
    elif inp == "automat":
        automat()
    else:
        print("Restart the program")


def automat():
    print('automat')
    
    rospy.Subscriber('scan', LaserScan, callback, queue_size=1)

    while not rospy.is_shutdown():

        filedescriptors = termios.tcgetattr(sys.stdin)
        tty.setcbreak(sys.stdin)
        x = 0

        x = sys.stdin.read(1)[0]

        if x == "o":
            control()
            break

    rospy.spin()


def callback(msg):

    alpha = 143
    rangos = msg.ranges
    rango4 = rangos[1:alpha]
    rango1 = rangos[alpha+1:2*alpha]
    rango2 = rangos[2*alpha+1:3*alpha]
    rango3 = rangos[3*alpha+1:4*alpha]

    R1 = any(((dist > 0) and (dist < 1.5)) for dist in rango1)
    R2 = any(((dist > 0) and (dist < 2)) for dist in rango2)
    R3 = any(((dist > 0) and (dist < 2)) for dist in rango3)
    R4 = any(((dist > 0) and (dist < 1.5)) for dist in rango4)

    if R1:

        if R2:

            P3 = np.mean(rango3)
            P4 = np.mean(rango4)

            if P3 > P4:

                angle = 40
                speed = vel+10
                message.linear.x = speed
                message.angular.z = angle
                pub.publish(message)
                print('Izquierda 90')
                print(message)
                #time.sleep(2)

            elif P4 > P3:
                angle = 90
                speed = vel
                message.linear.x = speed
                message.angular.z = angle
                pub.publish(message)
                print('Derecha 90')
                print(message)
                #time.sleep(2)

        else:
            angle = 40
            speed = vel+10
            message.linear.x = speed
            message.angular.z = angle
            pub.publish(message)
            print('Izquierda sutil, front')
            print(message)
            #time.sleep(1)
            #angle = 90
            #message.angular.z = angle
            #pub.publish(message)
            #print(message)
            #time.sleep(1)

    elif R2:

        angle = 140
        speed = vel
        message.linear.x = speed
        message.angular.z = angle
        pub.publish(message)
        print('Derecha sutil, front')
        print(message)
        #time.sleep(1)
        #angle = 90
        #message.angular.z = angle
        #pub.publish(message)
        #print(message)
        #time.sleep(1)

    elif R3:

        angle = 140
        speed = vel
        message.linear.x = speed
        message.angular.z = angle
        pub.publish(message)
        print('Derecha sutil')
        print(message)
        #time.sleep(1)
        #angle = 90
        #message.angular.z = angle
        #pub.publish(message)
        #print(message)
        #time.sleep(1)

    elif R4:

        angle = 40
        speed = vel+10
        message.linear.x = speed
        message.angular.z = angle
        pub.publish(message)
        print('Izquierda sutil')
        print(message)
        #time.sleep(1)
        #angle = 90
        #message.angular.z = angle
        #pub.publish(message)
        #print(message)
        #time.sleep(1)

    else:

        angle = 70
        speed = vel
        message.linear.x = speed
        message.angular.z = angle
        pub.publish(message)
        print('Normal')
        print(message)
        #time.sleep(1)


def manual_drive():  # You will use this function to program your ESC if required
    print("You have selected manual option so give a value between 0 and you max value")
    while True:
        inp = input()
        if inp == ("stop"):
            stop()
            break
        elif inp == ("control"):
            control()
            break
        elif inp == ("arm"):
            arm()
            break
        else:
            message.linear.x = inp
            pub.publish(message)


def calibrate():  # This is the auto calibration procedure of a normal ESC
    message.linear.x = 0
    message.linear.y = 0
    message.linear.z = 0
    message.angular.x = 0
    message.angular.y = 0
    message.angular.z = 0
    pub.publish(message)

    print("Disconnect the battery and press Enter")
    inp = input()

    if inp == '':
        message.linear.x = max_value
        pub.publish(message)
        print("Connect the battery NOW.. you will here two beeps, then wait for a gradual falling tone then press Enter")
        inp = input()
        if inp == '':
            message.linear.x = min_value
            pub.publish(message)
            print("Expected bep tone")
            time.sleep(2)
            print("Wait...")
            time.sleep(2)
            print("Wait...")
            message.linear.x = 0
            pub.publish(message)
            time.sleep(2)
            print("Arming ESC now...")
            message.linear.x = min_value
            pub.publish(message)
            time.sleep(1)
            print("Ready")
            control()  # You can change this to any other function you want


def control():
    print("Starting the motor, if not: restart by giving 'x'")
    time.sleep(1)
    speed = 1000  # change your speed if you want to.... it should be between 700 - 2000
    angle = 90
    print("Controls - a to turn left, -d to turn right, -w to speed up, -s to speed down, -p to stop, -o automat, -i arm.")
    rate = rospy.Rate(10)  # 10hz

    message.linear.x = speed
    message.angular.z = angle
    pub.publish(message)

    while not rospy.is_shutdown():

        filedescriptors = termios.tcgetattr(sys.stdin)
        tty.setcbreak(sys.stdin)
        x = 0

        x = sys.stdin.read(1)[0]

        if x == "s":
            if speed == 700:
                print("Minimum speed achieved (700)")
                message.linear.x = speed
                pub.publish(message)
            else:
                speed -= 20
                message.linear.x = speed
                pub.publish(message)

        elif x == "w":
            if speed == 2000:
                print("Maximum speed achieved (2000)")
                message.linear.x = speed
                pub.publish(message)
            else:
                speed += 20
                message.linear.x = speed
                pub.publish(message)

        elif x == "a":
            if angle == 40:
                print("Minimum angle achieved (40)")
                message.angular.z = angle
                pub.publish(message)
            else:
                angle -= 10
                message.angular.z = angle
                pub.publish(message)

        elif x == "d":
            if angle == 140:
                print("Maximum angle achieved (140)")
                message.angular.z = angle
                pub.publish(message)
            else:
                angle += 10
                message.angular.z = angle
                pub.publish(message)

        elif x == "p":
            stop()  # going for the stop function

        elif x == "o":
            automat()

        elif x == "i":
            arm()

        rospy.loginfo(message)
        rate.sleep()


def arm():  # This is the arming procedure of an ESC
    print("Connect the battery and press Enter")
    inp = input()
    if inp == '':
        message.linear.x = 0
        pub.publish(message)
        time.sleep(1)
        message.linear.x = max_value
        pub.publish(message)
        time.sleep(1)
        message.linear.x = min_value
        pub.publish(message)
        time.sleep(1)

        control()


def stop():  # This will stop every action your Pi is performing for ESC ofcourse.
    message.linear.x = 0
    pub.publish(message)
    rospy.loginfo(message)
    rospy.signal_shutdown('Stopped')


if __name__ == '__main__':
    try:
        hover_teleop()
    except rospy.ROSInterruptException:
        pass
