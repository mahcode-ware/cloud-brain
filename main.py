from fastapi import FastAPI, Request
import time
from motor.motor_asyncio import AsyncIOMotorClient
import uvicorn

app = FastAPI()

# 1. ACTUAL CLOUD CONNECTION
# Note: I added the database name "fraud_db" into the string
MONGO_DETAILS = "mongodb+srv://shanmathibubbly_db_user:WAhb2iWIhdYPEZ4S@ps11.ed5cswy.mongodb.net/fraud_db?retryWrites=true&w=majority&appName=ps11"

client = AsyncIOMotorClient(MONGO_DETAILS)
db = client.fraud_db
transaction_collection = db.get_collection("logs")

@app.get("/")
async def root():
    return {"message": "Cloud Brain is Online"}

@app.post("/analyze")
async def analyze_transaction(request: Request):
    data = await request.json()
    
    # 2. AI ANALYSIS LOGIC (The "Brain")
    # We assign risk based on amount and simulated anomaly detection
    risk_score = 0.1
    if data.get('amount', 0) > 40000:
        risk_score = 0.7  # High risk
    elif data.get('isKnownMaliciousIP') == True:
        risk_score = 0.9  # Critical risk
    
    # 3. PREPARE THE CLOUD LOG
    # We store everything the Edge sent us + our AI verdict
    log_entry = {
        "transactionId": data.get('transactionId'),
        "userId": data.get('userId'),
        "amount": data.get('amount'),
        "branch_location": data.get('location'),
        "ip_address": data.get('ipAddress'),
        "risk_score": risk_score,
        "verdict": "REJECT" if risk_score > 0.5 else "SECURE",
        "cloud_verified": True,
        "timestamp": time.time()
    }
    
    # 4. ASYNC INSERT TO MONGODB ATLAS
    try:
        await transaction_collection.insert_one(log_entry)
        print(f"☁️ [CLOUD] Saved Tx {log_entry['transactionId']} to MongoDB Atlas.")
    except Exception as e:
        print(f"❌ Database Error: {e}")

    # 5. RETURN RESPONSE TO EDGE NODE
    return {
        "verdict": log_entry["verdict"],
        "risk_score": risk_score,
        "cloud_timestamp": time.time(),
        "storage": "Distributed Cloud (Atlas)"
    }

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)