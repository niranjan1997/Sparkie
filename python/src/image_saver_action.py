#! /usr/bin/python


import rospy
from sensor_msgs.msg import Image
from cv_bridge import CvBridge, CvBridgeError
import cv2
import os


bridge = CvBridge()

def image_callback(msg):
    print("Received an image!")
    command = 'python3 client.py'
    try:
        cv2_img = bridge.imgmsg_to_cv2(msg, "bgr8")
    except CvBridgeError:
        pass
    else:
        cv2.imwrite('./img/tmp/tmp.jpg', cv2_img)
        rospy.sleep(1)
        os.system(command)

def main():
    rospy.init_node('image_listener')
    image_topic = "/camera/rgb/image_raw"
    rospy.Subscriber(image_topic, Image, image_callback)

    # rospy.spin()

if __name__ == '__main__':
    main()