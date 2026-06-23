from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
import uvicorn

from parser import AskonaParser
from database import Database


app = FastAPI(
    title="Askona Parser API",
    description="API for parsing products from Askona.ru website",
)

db = Database()

@app.get("/parse", summary="Start parsing products")
async def parse_askona(
    url: str = Query(..., description="URL of Askona catalog page"),
    count: int = Query(10, description="Number of items to be parsed", ge=1)
):
    
    parser = AskonaParser()
    try:
        products = parser.parse(url, count)
        if not products:
            raise HTTPException(status_code=400, detail="Failed to retrieve items from the page")
        
        db.save_products(products)
        return {
            "status": "success",
            "parsed_items": len(products),
            "message": f"Successfully sparred {len(products)} products"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        parser.close()

@app.get("/products", summary="Get product list")
async def get_products(
    limit: int = Query(10, description="Quantity of products", ge=1)
):

    try:
        products = db.get_products(limit)
        return products
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)