from fastapi import FastAPI, HTTPException, Header, Query, Body
from fastapi.responses import HTMLResponse
from pymongo import MongoClient

MONGO_URI = "mongodb+srv://week8:weekeight@week8.sncguyo.mongodb.net/"
DATABASE_NAME = "week8"
SECRET_KEY = "assign"

app = FastAPI()
client = MongoClient(MONGO_URI)
db = client[DATABASE_NAME]
sales_collection = db["sales"]

@app.get("/", response_class=HTMLResponse)
async def get_html():
    try : 
        with open("index.html", "r") as file:
            html_content = file.read()
        return HTMLResponse(content=html_content, status_code=200)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Route to handle the report request
@app.get("/report")
async def get_report(x_secret_key: str = Query(..., alias="X-Secret-Key")):
    if x_secret_key != SECRET_KEY:
        raise HTTPException(status_code=401, detail="Unauthorized")
    sales_report = list(sales_collection.find({}, {"_id": 0, "product": 1}))
    return {"sales_report": sales_report}


@app.post("/buy")
async def buy_product(product_info: dict = Body(...), x_secret_key: str = Header(None)):
    try :
        productName = product_info.get("product")
        if not productName:
            raise HTTPException(status_code=422, detail="Product name missing in request")
        if x_secret_key != SECRET_KEY:
            raise HTTPException(status_code=401, detail="Unauthorized")
        sales_collection.insert_one({"product": productName})
        return {"message": f"Successfully purchased {productName}"}
    except Exception as e:
        raise HTTPException(status_code=500, detail="Internal Server Error")
    
import uvicorn

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
