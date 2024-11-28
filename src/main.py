import socket
import struct
import csv
from proto import communication_pb2 as comm

MULTICAST_GROUP = '224.0.0.1'
ROBOT_IP = '199.0.1.1'
SEND_PORT = 19900
RECEIVE_PORT = 19901

def packet_available(sock):
    msg = comm.protoGlobalSpeedSSL()
    try:
        data, _ = sock.recvfrom(1024)

        if data:
            msg.ParseFromString(data)
            return True, msg
        
        return False, None

    except Exception as e:
        return False, None
    
def saveLog(data, csv_file):
    write_header = False
    
    try:
        with open(csv_file, "x", newline="") as file:
            write_header = True
    except FileExistsError:
        pass

    with open(csv_file, "a", newline="") as file:
        writer = csv.writer(file)

        if write_header:
            writer.writerow([
                "x", "y", "theta", "count",
                "packet_x", "packet_y", "packet_theta",
                "odometry_x", "odometry_y", "odometry_theta",
                "global_vx", "global_vy", "global_w",
                "local_vx", "local_vy", "local_w",
                "command_vx", "command_vy", "command_w"
            ])

        writer.writerow([
            data.x, data.y, data.theta, data.count,
            data.packet_x, data.packet_y, data.packet_theta,
            data.odometry_x, data.odometry_y, data.odometry_theta,
            data.global_vx, data.global_vy, data.global_w,
            data.local_vx, data.local_vy, data.local_w,
            data.command_vx, data.command_vy, data.command_w
        ])

def main():  

    robot_sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)
    robot_sock.setsockopt(socket.SOL_SOCKET, 25, struct.pack('16s', b'eth0'))
    robot_sock.bind((ROBOT_IP, RECEIVE_PORT))

    try:
        while True:
            newMsg, msg = packet_available(robot_sock)
        
            if newMsg:
                print(f"Received from PC")
                saveLog(msg, "log_position.csv")

    except KeyboardInterrupt:
        print("\nExiting...")

    robot_sock.close()

if __name__ == "__main__":
    main()