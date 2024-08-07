import socket
import time

from proto import RComm_pb2 as rcomm

TEAM_NAME = "ROBOCIN"

def send_request(sock, multicast_group, port):
    _msgPublish = rcomm.DiscoveryRequest()
    _msgPublish.robot_id = 1
    _msgPublish.team_name = TEAM_NAME
    serialized_msg = _msgPublish.SerializeToString()
    
    sock.sendto(serialized_msg, (multicast_group, port))

def main():
    ip_pc = None
    multicast_group = '224.0.0.1'
    port = 19900

    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)
    sock.setsockopt(socket.IPPROTO_IP, socket.IP_MULTICAST_TTL, 255)

    while ip_pc is None:
        send_request(sock, multicast_group, port)
        print(f"Mensagem enviada para {multicast_group}:{port}")
        time.sleep(0.2)

    sock.close()

if __name__ == "__main__":
    main()