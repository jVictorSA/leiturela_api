from pymongo import MongoClient

# Replace these with your MongoDB connection details
# MongoDB username
# MongoDB Password
# MongoDB hosting type
# Default port of MongoDB is 27017
# MongoDB Database name
MONGO_USERNAME = "storyUser"
MONGO_PASSWORD = "u9zA0qr*"
MONGO_HOST = "localhost"
MONGO_PORT = 27017
MONGO_DB = "stories_db"

# Create a MongoDB client
client = MongoClient(
	f"mongodb://{MONGO_USERNAME}:{MONGO_PASSWORD}@{MONGO_HOST}:{MONGO_PORT}/{MONGO_DB}")
db = client[MONGO_DB]
