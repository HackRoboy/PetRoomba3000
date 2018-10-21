#!/usr/bin/env python
# USAGE
# python real_time_object_detection.py --prototxt MobileNetSSD_deploy.prototxt.txt --model MobileNetSSD_deploy.caffemodel

# import the necessary packages
from imutils.video import VideoStream
from imutils.video import FPS
import numpy as np
import argparse
import imutils
import time
import cv2
import rospy
from geometry_msgs.msg import Twist
from std_msgs.msg import Int8
import math

turn = 1
_maximum_width = 400
_camera_angle = 60

# ROS stuff
pub_turtlesim = rospy.Publisher('commands', Twist, queue_size=10)
pub_roomba = rospy.Publisher('roomba', Int8, queue_size=10)
rospy.init_node('publisher', anonymous=True)
rate = rospy.Rate(10) # 10hz
cmd_vel = Twist()
cmd_roomba = Int8()

def calculate_angle(startX, startY, endX, endY):
	#print(turn)
	turn = 0
	locationX = endX - (endX-startX)/2
	angle_coordinates = locationX-_maximum_width/2
	angle_degree = (angle_coordinates / float(_maximum_width)) * _camera_angle
	angle_radiants = angle_degree/360 * 2 * float(math.pi)
	angular_speed = 2*math.pi/10
	print("steering_angle = "+str(angle_degree))

	if (abs(angle_degree) < _camera_angle/2):
        	cmd_vel.linear.x = 0.0
            	cmd_vel.linear.y = 0.0
            	cmd_vel.linear.z = 0.0
            	cmd_vel.angular.x = 0.0
            	cmd_vel.angular.y = 0.0
		cmd_vel.angular.z = angular_speed

		#cmd_roomba.forward = False
		cmd_roomba.data = 6
		
		if (angle_degree > 0):
			#cmd_roomba.right = False
			#cmd_roomba.left = True
			cmd_roomba.data = 4
		else:
			#cmd_roomba.right = True
			#cmd_roomba.left = False
			cmd_roomba.data = 5



            	t0 = rospy.Time.now().to_sec()
	     	current_angle = 0.0
		print(current_angle, angle_radiants)
    		while(current_angle < abs(angle_radiants)):
         		pub_turtlesim.publish(cmd_vel)
			pub_roomba.publish(cmd_roomba)
         		t1 = rospy.Time.now().to_sec()
        		current_angle = angular_speed*(t1-t0)
        else:
		cmd_vel.linear.x = 0.0
	    	cmd_vel.linear.y = 0.0
	    	cmd_vel.linear.z = 0.0
	   	cmd_vel.angular.x = 0.0
	    	cmd_vel.angular.y = 0.0
	    	cmd_vel.angular.z = 0.0

		#cmd_roomba.forward = False
		#cmd_roomba.right = False
		#cmd_roomba.left = False
		cmd_roomba.data = 6

        	pub_turtlesim.publish(cmd_vel)
		pub_roomba.publish(cmd_roomba)
	

def check_bottle_area (startX, startY, endX, endY):
	area_covered = (endX-startX)*(endY-startY)/_maximum_width/float(_maximum_width)
	print("area covered = "+str(area_covered))
	
    	cmd_vel.linear.y = 0.0
    	cmd_vel.linear.z = 0.0
    	cmd_vel.angular.x = 0.0
    	cmd_vel.angular.y = 0.0
	cmd_vel.angular.z = 0.0

	#cmd_roomba.right = False
	#cmd_roomba.left = False

	if(area_covered>0.2):
            	cmd_vel.linear.x = 0.0
		#cmd_roomba.forward = False
		cmd_roomba.data = 6
	else:
		cmd_vel.linear.x = 1.0
		#cmd_roomba.forward = True
		cmd_roomba.data = 1

	pub_turtlesim.publish(cmd_vel)
	pub_roomba.publish(cmd_roomba)

# construct the argument parse and parse the arguments
ap = argparse.ArgumentParser()
ap.add_argument("-p", "--prototxt", default="MobileNetSSD_deploy.prototxt.txt",
	help="path to Caffe 'deploy' prototxt file")
ap.add_argument("-m", "--model", default="MobileNetSSD_deploy.caffemodel",
	help="path to Caffe pre-trained model")
ap.add_argument("-c", "--confidence", type=float, default=0.2,
	help="minimum probability to filter weak detections")
args = vars(ap.parse_args())

# initialize the list of class labels MobileNet SSD was trained to
# detect, then generate a set of bounding box colors for each class
CLASSES = ["background", "aeroplane", "bicycle", "bird", "boat",
	"bottle", "bus", "car", "cat", "chair", "cow", "diningtable",
	"dog", "horse", "motorbike", "person", "pottedplant", "sheep",
	"sofa", "train", "tvmonitor"]
COLORS = np.random.uniform(0, 255, size=(len(CLASSES), 3))

# load our serialized model from disk
print("[INFO] loading model...")
net = cv2.dnn.readNetFromCaffe(args["prototxt"], args["model"])

# initialize the video stream, allow the cammera sensor to warmup,
# and initialize the FPS counter
print("[INFO] starting video stream...")
vs = VideoStream(src=0).start()
# vs = VideoStream(usePiCamera=True).start()
time.sleep(2.0)
fps = FPS().start()

# loop over the frames from the video stream
#while True:
while not rospy.is_shutdown():
	# grab the frame from the threaded video stream and resize it
	# to have a maximum width of 400 pixels
	frame = vs.read()
	frame = imutils.resize(frame, width=_maximum_width)

	# grab the frame dimensions and convert it to a blob
	(h, w) = frame.shape[:2]
	blob = cv2.dnn.blobFromImage(cv2.resize(frame, (300, 300)),
		0.007843, (300, 300), 127.5)

	# pass the blob through the network and obtain the detections and
	# predictions
	net.setInput(blob)
	detections = net.forward()

	# loop over the detections

	bottle_found = False
	for i in np.arange(0, detections.shape[2]):
		# extract the confidence (i.e., probability) associated with
		# the prediction
		confidence = detections[0, 0, i, 2]
		

		# filter out weak detections by ensuring the `confidence` is
		# greater than the minimum confidence
		if confidence > args["confidence"]:
			# extract the index of the class label from the
			# `detections`, then compute the (x, y)-coordinates of
			# the bounding box for the object
			idx = int(detections[0, 0, i, 1])
			box = detections[0, 0, i, 3:7] * np.array([w, h, w, h])
			(startX, startY, endX, endY) = box.astype("int")

			# draw the prediction on the frame
			label = "{}: {:.2f}%".format(CLASSES[idx],
				confidence * 100)
			cv2.rectangle(frame, (startX, startY), (endX, endY),
				COLORS[idx], 2)
			y = startY - 15 if startY - 15 > 15 else startY + 15
			cv2.putText(frame, label, (startX, y),
				cv2.FONT_HERSHEY_SIMPLEX, 0.5, COLORS[idx], 2)
			if(CLASSES[idx]=="bottle"  and turn==1):
				calculate_angle(startX, startY, endX, endY)
				turn = 0
			if(CLASSES[idx]=="bottle"):
				check_bottle_area(startX, startY, endX, endY)
				bottle_found = True

	if(not(bottle_found)):
		print("No bottle has been detected")
		cmd_vel.linear.x = 0.0
	    	cmd_vel.linear.y = 0.0
	    	cmd_vel.linear.z = 0.0
	   	cmd_vel.angular.x = 0.0
	    	cmd_vel.angular.y = 0.0
	    	cmd_vel.angular.z = 0.0
        	pub_turtlesim.publish(cmd_vel)

	# show the output frame
	cv2.imshow("Frame", frame)
	key = cv2.waitKey(1) & 0xFF

	# if the `q` key was pressed, break from the loop
	if key == ord("q"):
		break

	# update the FPS counter
	fps.update()

# stop the timer and display FPS information
fps.stop()
print("[INFO] elapsed time: {:.2f}".format(fps.elapsed()))
print("[INFO] approx. FPS: {:.2f}".format(fps.fps()))

# do a bit of cleanup
cv2.destroyAllWindows()
vs.stop()
