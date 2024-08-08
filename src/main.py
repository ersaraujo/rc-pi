import socket
import struct
import time
from proto import RComm_pb2 as rcomm

TEAM_NAME = "ROBOCIN"

MULTICAST_GROUP = '224.0.0.1'
ROBOT_IP = '199.0.1.1'
SEND_PORT = 19900
RECEIVE_PORT = 19901

def send_request(sock):
    _msgPublish = rcomm.DiscoveryRequest()
    _msgPublish.robot_id = 1
    _msgPublish.team_name = TEAM_NAME
    serialized_msg = _msgPublish.SerializeToString()
    
    sock.sendto(serialized_msg, (MULTICAST_GROUP, SEND_PORT))

def receive_response(sock):
    try:
        sock.settimeout(5.0)
        data, addr = sock.recvfrom(1024)
        
        msg = rcomm.DiscoveryResponse() 
        msg.ParseFromString(data)
        
        print(f"Resposta recebida de {addr}:")
        print(f"Team: {msg.team_name}")
        print(f"Team Color: {msg.team_color}")

        return addr[0]
    
    except socket.timeout:
        print("timout")
        send_request(sock)

def packet_available(sock):
    while True:
        data, _ = sock.recvfrom(1024)
        
        if data:
            msg = rcomm.SSLSpeed()
            
            return True, msg
        
        return False, None

def send2robot(msg, sock):
    serialized_msg = msg.SerializeToString()
    sock.sendto(serialized_msg, (ROBOT_IP, SEND_PORT))

def main():
    ip_pc = None
    
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
            newMsg, msg = packet_available(pc_sock)
        
            if newMsg:
                print(f"Received from PC: {msg}")
                send2robot(msg, robot_sock)

        except KeyboardInterrupt:
            break

    pc_sock.close()
    robot_sock.close()

if __name__ == "__main__":
    main()