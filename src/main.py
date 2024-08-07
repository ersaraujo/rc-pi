import socket
import struct
import time
from proto import RComm_pb2 as rcomm

TEAM_NAME = "ROBOCIN"

MULTICAST_GROUP = '224.0.0.1'
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

def main():
    ip_pc = None
    
    # Configura o socket para enviar mensagens
    send_sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)
    send_sock.setsockopt(socket.IPPROTO_IP, socket.IP_MULTICAST_TTL, 255)
    
    receive_sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)
    receive_sock.bind(('', RECEIVE_PORT))
    receive_sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    
    mreq = struct.pack('4sl', socket.inet_aton(MULTICAST_GROUP), socket.INADDR_ANY)
    receive_sock.setsockopt(socket.IPPROTO_IP, socket.IP_ADD_MEMBERSHIP, mreq)
    
    while ip_pc is None:
        ip_pc = receive_response(receive_sock)

    send_sock.close()
    receive_sock.close()

if __name__ == "__main__":
    main()
