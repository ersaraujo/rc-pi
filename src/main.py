import socket
import struct
import time
from proto import robot_info_pb2 as core
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
    msg = core.RobotInfo()
    try:
        data, _ = sock.recvfrom(1024)

        if data:
            msg.ParseFromString(data)  # Deserializa a mensagem recebida
            return True, msg
        
        return False, None

    except Exception as e:
        return False, None
    
def make_command(msg):
    msg2send = rcomm.SSLSpeed()
    for command in msg.output.command:
        if command.robot_id.number == 1:
            msg2send.id = command.robot_id.number
            
            msg2send.vx = command.robot_velocity.velocity.x
            msg2send.vy = command.robot_velocity.velocity.y
            msg2send.vw = command.robot_velocity.angular_velocity
            
            msg2send.front = command.kick_command.is_front
            msg2send.chip = command.kick_command.is_chip
            msg2send.charge = command.kick_command.charge_capacitor
            msg2send.kickStrength = command.kick_command.kick_strength

            msg2send.dribbler = command.dribbler_command.is_active
            msg2send.dribSpeed = command.dribbler_command.dribbler_speed

    print(f"Command to send: {msg2send}")
    return msg2send

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
    # robot_sock.setsockopt(socket.SOL_SOCKET, 25, struct.pack('16s', b'wlo'))

    while True:
        try:
            newMsg, msg = packet_available(pc_sock)
        
            if newMsg:
                # print(f"Received from PC: {msg}")
                send2robot(make_command(msg), robot_sock)

        except KeyboardInterrupt:
            break

    pc_sock.close()
    # robot_sock.close()

if __name__ == "__main__":
    main()