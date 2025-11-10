from fastapi import FastAPI, HTTPException, Query, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from datetime import datetime
from typing import Optional
import uvicorn
import os

from data_manager import data_manager

app = FastAPI(
    title="MegaMart Supermarket API",
    description="API for MegaMart Supermarket competitor intelligence",
    version="1.0.0"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
async def root():
    return {
        "message": "MegaMart Supermarket API is running!",
        "version": "1.0.0",
        "endpoints": {
            "competitor_pricing": "/api/competitor-pricing",
            "competitor_summary": "/api/competitor-pricing/summary",
            "health": "/api/health"
        }
    }

@app.get("/api/health")
async def health_check():
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "data_loaded": len(data_manager.competitor_data)
    }

@app.get("/api/competitor-pricing")
async def get_competitor_pricing(
    competitor: Optional[str] = Query(None),
    category: Optional[str] = Query(None),
    date: Optional[str] = Query(None),
    limit: int = Query(100, ge=1, le=1000),
    offset: int = Query(0, ge=0)
):
    try:
        filtered_data = data_manager.competitor_data
        
        if competitor:
            filtered_data = [item for item in filtered_data 
                           if item.get('competitor_name', '').lower() == competitor.lower()]
        
        if category:
            filtered_data = [item for item in filtered_data 
                           if item.get('product_category', '').lower() == category.lower()]
        
        if date:
            filtered_data = [item for item in filtered_data 
                           if item.get('scrape_date') == date]
        
        paginated_data = filtered_data[offset:offset + limit]
        
        return {
            "data": paginated_data,
            "pagination": {
                "total": len(filtered_data),
                "limit": limit,
                "offset": offset,
                "returned": len(paginated_data)
            }
        }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error: {str(e)}")

@app.get("/api/competitor-pricing/summary")
async def get_competitor_summary(date: Optional[str] = Query(None)):
    try:
        filtered_data = data_manager.competitor_data
        
        if date:
            filtered_data = [item for item in filtered_data if item.get('scrape_date') == date]
        
        competitor_summary = {}
        
        for item in filtered_data:
            competitor = item['competitor_name']
            if competitor not in competitor_summary:
                competitor_summary[competitor] = {
                    "competitor_name": competitor,
                    "total_categories": 0,
                    "average_price_index": 0,
                    "total_products": 0
                }
            
            competitor_summary[competitor]["total_categories"] += 1
            competitor_summary[competitor]["average_price_index"] += item["overall_price_index"]
            competitor_summary[competitor]["total_products"] += len(item.get("products_monitored", []))
        
        # Calculate averages
        for competitor in competitor_summary:
            total_categories = competitor_summary[competitor]["total_categories"]
            if total_categories > 0:
                competitor_summary[competitor]["average_price_index"] = round(
                    competitor_summary[competitor]["average_price_index"] / total_categories, 2
                )
        
        return {
            "total_competitors": len(competitor_summary),
            "total_records": len(filtered_data),
            "competitors": list(competitor_summary.values())
        }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error: {str(e)}")

@app.get("/api/competitor-pricing/competitors")
async def get_competitors():
    try:
        competitors = list(set(item['competitor_name'] for item in data_manager.competitor_data))
        return {"competitors": sorted(competitors)}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error: {str(e)}")

@app.get("/api/competitor-pricing/categories")
async def get_categories():
    try:
        categories = list(set(item['product_category'] for item in data_manager.competitor_data))
        return {"categories": sorted(categories)}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error: {str(e)}")

@app.post("/api/competitor-pricing/reload")
async def reload_data():
    data_manager.reload_data()
    return {"message": "Data reloaded", "records": len(data_manager.competitor_data)}

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)