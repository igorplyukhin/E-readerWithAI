from fastapi import APIRouter, HTTPException, status
from fastapi.responses import JSONResponse

# Assume necessary imports for database interaction (e.g., pymongo) are available. Replace with your actual implementations.

test_router = APIRouter()

@test_router.post("/health")
async def health_check():
    try:
        users_collection = DatabaseFactory.get_users_collection()
        count = await users_collection.count_documents({}) # Assuming you are using an async driver
        return JSONResponse(status_code=status.HTTP_200_OK, content={"message": f"Connected to MongoDB. Users count: {count}"})
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to connect to MongoDB")


# Placeholder for DatabaseFactory - replace with your actual implementation
class DatabaseFactory:
    @staticmethod
    def get_users_collection():
        return None # Replace with your database collection object