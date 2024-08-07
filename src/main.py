from proto import RComm_pb2 as rcomm

def main():
    _msgPublish = rcomm.DiscoveryRequest()
    _msgPublish.robot_id = 1
    _msgPublish.team_name = "Test"

    print(_msgPublish)


if __name__ == "__main__":
    main()