import readchar

import rospy
from std_msgs.msg import Int8


def talker():
    pub = rospy.Publisher('pet_roomba300', Int8, queue_size=10)
    rospy.init_node('RoombaWASD', anonymous=True)
    rate = rospy.Rate(10) # 10hz
    while not rospy.is_shutdown():
        key = readchar.readkey()
        key = key.lower()

        if key in ('wasd'):
            if key == 'w':  # Forward
                pub.publish(1)
            elif key == 'a'  # Left
                pub.publish(4)
            elif key == 'd'  # Right
                pub.publish(5)
            elif key == 's'  # stand still
                pub.publish(6)
        elif key == 'p':
            print "stop"
            break
        rate.sleep()

if __name__ == '__main__':
    try:
        talker()
    except rospy.ROSInterruptException:
        pass

