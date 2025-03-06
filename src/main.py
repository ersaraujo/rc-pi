import socket
import random
import time
import struct

from proto import communication_pb2 as comm

MULTICAST_GROUP = '224.0.0.1'
SEND_PORT = 19900
    
def generate_feedback():
    feedback = comm.Feedback()
    
    feedback.id = random.randint(0, 15)

    feedback.battery = round(random.uniform(6.0, 8.4), 2)
    feedback.kickLoad = round(random.uniform(0.0, 5.0), 2) 
    feedback.irBall = random.choice([True, False])

    feedback.velocity.m1 = round(random.uniform(-50.0, 50.0), 2)
    feedback.velocity.m2 = round(random.uniform(-50.0, 50.0), 2)
    feedback.velocity.m3 = round(random.uniform(-50.0, 50.0), 2)
    feedback.velocity.m4 = round(random.uniform(-50.0, 50.0), 2)

    feedback.current.m1 = round(random.uniform(0.0, 2.0), 2)
    feedback.current.m2 = round(random.uniform(0.0, 2.0), 2)
    feedback.current.m3 = round(random.uniform(0.0, 2.0), 2)
    feedback.current.m4 = round(random.uniform(0.0, 2.0), 2)

    feedback.timestamp = int(time.time() * 1e3)

    print(feedback)

    return feedback

def send_feedback(msg, sock):
    serialized_msg = msg.SerializeToString()
    sock.sendto(serialized_msg, (MULTICAST_GROUP, SEND_PORT))

def main():
    pc_sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)
    mreq = struct.pack('4sl', socket.inet_aton(MULTICAST_GROUP), socket.INADDR_ANY)
    
    pc_sock.setsockopt(socket.IPPROTO_IP, socket.IP_MULTICAST_TTL, 255)
    pc_sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    pc_sock.setsockopt(socket.IPPROTO_IP, socket.IP_ADD_MEMBERSHIP, mreq)
    
    while True:
        try:
            msg = generate_feedback()
            send_feedback(msg, pc_sock)
            time.sleep(1/90)

        except KeyboardInterrupt:
            break

    pc_sock.close()

if __name__ == "__main__":
    main()