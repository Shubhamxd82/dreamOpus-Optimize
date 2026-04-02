from motor.motor_asyncio import AsyncIOMotorClient
from info import DATABASE_URI, DATABASE_NAME

# Single shared MongoDB client for the entire application
# Reduces from 5 separate connection pools (500 potential connections) to 1 (50 connections)
mongo_client = AsyncIOMotorClient(DATABASE_URI, maxPoolSize=50)
db = mongo_client[DATABASE_NAME]
