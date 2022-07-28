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

os.system("sudo pigpiod")  # Launching GPIO library


ESC = 4  # Connect the ESC in this GPIO pin

pi = pigpio.pi()
pi.set_servo_pulsewidth(ESC, 0)

servo = Servo(25)
servo.value = 0
val = 0

def callback(msg):

    speed = msg.linear.x
    angle = msg.angular.z
    pi.set_servo_pulsewidth(ESC, speed)
    val = (-0.019*angle)+1.8
servo.value = val


def hover_motors():

    # In ROS, nodes are uniquely named. If two nodes with the same
    # name are launched, the previous one is kicked off. The
    # anonymous=True flag means that rospy will choose a unique
    # name for our 'listener' node so that multiple listeners can
    # run simultaneously.

    rospy.init_node('hover_motors', anonymous=True)

    rospy.Subscriber('cmd_vel', Twist, callback)

    # spin() simply keeps python from exiting until this node is stopped
    rospy.spin()


if __name__ == '__main__':
    hover_motors()
