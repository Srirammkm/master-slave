import time
import grpc
from getLogWindows import Windows
from datetime import datetime, timezone
import streamer_pb2
import streamer_pb2_grpc
import config

def init_session(channel, date, start_time, os_platform, os_version, username, orgid):
    stub = streamer_pb2_grpc.StreamLogServiceStub(channel)
    request = streamer_pb2.InitLogRequest(
        date=date,
        start_time=start_time,
        os_platform=os_platform,
        os_version=os_version,
        username=username,
        orgid=orgid,
    )
    response = stub.InitLogData(request)
    print(f"response from master: {response.message}")


def stream_log(host, date, start_time, orgid):
    lapsed_time = 5
    while True:
        try:
            time.sleep(lapsed_time)
            app, alias = host.get_active_application()
            username = host.username
            agent_last_online = datetime.now().strftime("%Y-%m-%d-%H:%M:%S")
            user_last_online = datetime.now().strftime("%Y-%m-%d-%H:%M:%S")
            session_usage = streamer_pb2.StreamLogRequest(
                date=date,
                start_time=start_time,
                app=app,
                alias=alias,
                lapsed=lapsed_time,
                agent_last_online=agent_last_online,
                user_last_online=user_last_online,
                username=username,
                orgid=orgid,
            )
            print(f"stream to spectrawatch: {app} is lapsed for {lapsed_time} seconds")
            yield session_usage
        except Exception as e:
            print(e)

def stream_session(channel, host, date, start_time, orgid):
    stub = streamer_pb2_grpc.StreamLogServiceStub(channel)
    try:
        _reply = stub.StreamLogData(stream_log(host, date, start_time, orgid))
        print(f"response from master: {_reply.message}")
    except Exception as e:
        print(e)


if __name__ == "__main__":
    with grpc.insecure_channel(
       config.SPECTRAWATCH_ENDPOINT+":"+config.SPECTRAWATCH_PORT
    ) as channel:  # insecure channel for dev
        host_device = Windows()
        current_datetime = datetime.now()
        date = current_datetime.strftime("%Y-%m-%d")
        start_time = datetime.now().strftime("%Y-%m-%d-%H:%M:%S")
        init_session(
            channel=channel,
            date=date,
            start_time=start_time,
            os_platform=host_device.os_platform,
            os_version=host_device.os_version,
            username=host_device.username,
            orgid=config.ORG_ID,
        )
        stream_session(
            channel=channel,
            host=host_device,
            date=date,
            start_time=start_time,
            orgid=config.ORG_ID,
        )
