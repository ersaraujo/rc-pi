import socket
import struct
import time
from proto import RComm_pb2 as rcomm

TEAM_NAME = "ROBOCIN"
BLUE_TEAM = 1

MULTICAST_GROUP = '224.0.0.1'
RECEIVE_PORT = 19900
SEND_PORT = 19901

def main():
    robot_sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)
    mreq = struct.pack('4sl', socket.inet_aton(MULTICAST_GROUP), socket.INADDR_ANY)
    
    robot_sock.setsockopt(socket.IPPROTO_IP, socket.IP_MULTICAST_TTL, 255)
    robot_sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    robot_sock.setsockopt(socket.IPPROTO_IP, socket.IP_ADD_MEMBERSHIP, mreq)
    
    robot_sock.bind(('', RECEIVE_PORT))
    
    while True:
        msg2robot = rcomm.SSLSpeed()

        msg2robot.id = 1
        msg2robot.vx = 0.0
        msg2robot.vy = 0.0
        msg2robot.vw = 3.5
        msg2robot.front = False
        msg2robot.chip = False
        msg2robot.charge = False
        msg2robot.kickStrength = 0.0
        msg2robot.dribbler = False
        msg2robot.dribSpeed = 0.0

        serialized_msg = msg2robot.SerializeToString()
        robot_sock.sendto(serialized_msg, (MULTICAST_GROUP, SEND_PORT))

        time.sleep(0.05)
        

if __name__ == "__main__":
    main()