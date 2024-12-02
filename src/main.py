import socket
import struct
import keyboard
from proto import communication_pb2 as comm

TEAM_NAME = "ROBOCIN"

MULTICAST_GROUP = '224.0.0.1'
ROBOT_IP = '199.0.1.1'
SEND_PORT = 19900
RECEIVE_PORT = 19901 

def send2robot(msg, sock):
    serialized_msg = msg.SerializeToString()
    sock.sendto(serialized_msg, (ROBOT_IP, SEND_PORT))


def handle_keyboard_commands(sock):
    command = comm.OutputRobot()

    while True:
        try:
            if keyboard.is_pressed('w'):
                command.vx = 1.0
                command.vy = 0.0
                command.vw = 0.0
                print("forward")
            elif keyboard.is_pressed('s'):
                command.vx = -1.0
                command.vy = 0.0
                command.vw = 0.0
                print("backward")
            elif keyboard.is_pressed('a'):
                command.vx = 0.0
                command.vy = -1.0
                command.vw = 0.0
                print("left")
            elif keyboard.is_pressed('d'):
                command.vx = 0.0
                command.vy = 1.0
                command.vw = 0.0
                print("right")
            elif keyboard.is_pressed('q'):
                command.vx = 0.0
                command.vy = 0.0
                command.vw = 2.0
                print("cw")
            elif keyboard.is_pressed('e'):
                command.vx = 0.0
                command.vy = 0.0
                command.vw = -2.0
                print("ccw")
            elif keyboard.is_pressed('x'):
                break
            else:
                command.vx = 0.0
                command.vy = 0.0
                command.vw = 0.0
            send2robot(command, sock)
        except KeyboardInterrupt:
            print("\nKeyboard interrupted!")
            break


def main():
    pc_sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)
    mreq = struct.pack('4sl', socket.inet_aton(MULTICAST_GROUP), socket.INADDR_ANY)
    
    pc_sock.setsockopt(socket.IPPROTO_IP, socket.IP_MULTICAST_TTL, 255)
    pc_sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    pc_sock.setsockopt(socket.IPPROTO_IP, socket.IP_ADD_MEMBERSHIP, mreq)
    pc_sock.bind(('', RECEIVE_PORT))    

    robot_sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)
    robot_sock.setsockopt(socket.SOL_SOCKET, 25, struct.pack('16s', b'eth0'))

    while True:
        try:
            handle_keyboard_commands(robot_sock)

        except KeyboardInterrupt:
            break

    pc_sock.close()
    robot_sock.close()


if __name__ == "__main__":
    main()
