import os
import logging
from pymongo import MongoClient, errors

logger = logging.getLogger(__name__)

class DatabaseFactory:
    _mongo_client = None
    _database = None

    @classmethod
    def init(cls):
        try:
            uri = os.environ.get("MONGODB_URI", "mongodb://mongo:27018/bookdb")
            db_name = "bookdb" # Or extract from connection string if needed.

            logger.info(f"Initializing MongoDB connection with URI: {uri}")
            cls._mongo_client = MongoClient(uri)
            cls._database = cls._mongo_client[db_name]
            logger.info(f"MongoDB connection established successfully. Database used: {db_name}")

        except errors.ConnectionFailure as e:
            logger.error(f"Error connecting to MongoDB: {e}")
            raise  # Re-raise the exception to halt application startup.


    @classmethod
    def getUsersCollection(cls):
        cls._ensure_initialized()
        return cls._database["users"]

    @classmethod
    def getBooksCollection(cls):
        cls._ensure_initialized()
        return cls._database["books"]

    @classmethod
    def getTextBlocksCollection(cls):
        cls._ensure_initialized()
        return cls._database["text_blocks"]

    @classmethod
    def close(cls):
        if cls._mongo_client:
            logger.info("Closing MongoDB connection...")
            cls._mongo_client.close()
            logger.info("MongoDB connection closed.")

    @classmethod
    def _ensure_initialized(cls):
        if not cls._mongo_client or not cls._database:
            raise RuntimeError("DatabaseFactory not initialized. Call DatabaseFactory.init() before use.")


#Example usage (Remember to configure logging appropriately):
#logging.basicConfig(level=logging.INFO)
#DatabaseFactory.init()
#users_collection = DatabaseFactory.getUsersCollection()
#DatabaseFactory.close()