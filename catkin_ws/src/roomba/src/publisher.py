#!/usr/bin/env python
import rospy
from geometry_msgs.msg import Twist

def publisher():
    pub = rospy.Publisher('commands', Twist, queue_size=10)
    rospy.init_node('publisher', anonymous=True)
    rate = rospy.Rate(10) # 10hz
    cmd_vel = Twist()
    while not rospy.is_shutdown():
        #angle = 10.0
        if (abs(angle) < 30.0 and abs(angle) > 2.0):
            cmd_vel.linear.x = 1.0
            cmd_vel.linear.y = 0.0
            cmd_vel.linear.z = 0.0
            cmd_vel.angular.x = 0.0
            cmd_vel.angular.y = 0.0
            cmd_vel.angular.z = 2.0
        else:
            cmd_vel.linear.x = 0.0
            cmd_vel.linear.y = 0.0
            cmd_vel.linear.z = 0.0
            cmd_vel.angular.x = 0.0
            cmd_vel.angular.y = 0.0
            cmd_vel.angular.z = 0.0
        pub.publish(cmd_vel)
    rate.sleep()

if __name__ == '__main__':
    try:
        publisher()
    except rospy.ROSInterruptException:
        pass
