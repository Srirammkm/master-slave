from concurrent import futures
import grpc
from pymongo import MongoClient
import logging
import streamer_pb2
import streamer_pb2_grpc


# Configure logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

# MongoDB setup
client = MongoClient("mongodb://localhost:27017/")


class StreamLogServicer(streamer_pb2_grpc.StreamLogServiceServicer):
    def InitLogData(self, request, context):
        date: str = request.date
        orgid: str = request.orgid
        username: str = request.username
        start_time: str = request.start_time
        os_version: str = request.os_version
        os_platform: str = request.os_platform
        logger.info(f"[{orgid}] initializing for [{username}] at {start_time}")
        db = client[orgid]
        collection = db[username]
        document = collection.find_one({"date": date})
        if document:
            collection.update_one({"date": date}, {"$push": {"start_time": start_time}})
            collection.update_one(
                {"date": date}, {"$set": {f"application_usage.{start_time}": {}}}
            )
            return streamer_pb2.InitLogResponse(
                status=True, message="Existing Document updated successfully."
            )
        else:
            collection.insert_one(
                {
                    "date": date,
                    "start_time": [start_time],
                    "os_platform": os_platform,
                    "os_version": os_version,
                }
            )
            collection.update_one(
                {"date": date}, {"$set": {f"application_usage.{start_time}": {}}}
            )
            return streamer_pb2.InitLogResponse(
                status=True, message="New Document created successfully."
            )

    def StreamLogData(self, request_iterator, context):
        for request in request_iterator:
            logger.info(f"Received application usage data from {request.username}")
            date: str = request.date
            start_time: str = request.start_time
            agent_last_online: str = request.agent_last_online
            user_last_online: str = request.user_last_online
            app_name: str = request.app
            alias: str = request.alias
            lapsed_time: str = request.lapsed
            username: str = request.username
            orgid: str = request.orgid
            db = client[orgid]
            collection = db[username]
            update_operations = {
                "$set": {
                    "agent_last_online": agent_last_online,
                    "user_last_online": user_last_online,
                    f"application_usage.{start_time}.{app_name}.alias": alias
                },
                "$inc": {
                    f"application_usage.{start_time}.{app_name}.lapsed_time": lapsed_time
                }
            }
            collection.update_one(
                {"date": date},
                update_operations,
                upsert=True,
            )
        return streamer_pb2.StreamLogResponse(
            status=True, message="Data stream processed successfully"
        )


def serve():
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    streamer_pb2_grpc.add_StreamLogServiceServicer_to_server(
        StreamLogServicer(), server
    )
    server.add_insecure_port("[::]:50051")
    logger.info("starting gRPC server on port 50051.")
    server.start()
    server.wait_for_termination()


if __name__ == "__main__":
    serve()
