from fastapi import FastAPI, HTTPException, Query, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from datetime import datetime, date
from typing import Optional, List, Dict, Any
import uvicorn
import os

from data_manager import data_manager

app = FastAPI(
    title="MegaMart Supermarket Competitor Intelligence API",
    description="Real-time API for competitor pricing intelligence and market analysis",
    version="2.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify actual origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
async def root():
    return {
        "message": "🏪 MegaMart Competitor Intelligence API",
        "version": "2.0.0",
        "status": "running",
        "timestamp": datetime.now().isoformat(),
        "endpoints": {
            "competitor_pricing": "/api/competitor-pricing",
            "competitor_summary": "/api/competitor-pricing/summary",
            "competitors_list": "/api/competitor-pricing/competitors",
            "categories_list": "/api/competitor-pricing/categories",
            "dates_list": "/api/competitor-pricing/dates",
            "health": "/api/health",
            "stats": "/api/stats"
        }
    }

@app.get("/api/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "data_loaded": len(data_manager.competitor_data),
        "data_source": data_manager.data_file or "sample_data"
    }

@app.get("/api/stats")
async def get_stats():
    """Get API statistics"""
    competitors = data_manager.get_competitors()
    categories = data_manager.get_categories()
    dates = data_manager.get_dates()
    
    return {
        "total_records": len(data_manager.competitor_data),
        "total_competitors": len(competitors),
        "total_categories": len(categories),
        "date_range": {
            "earliest": min(dates) if dates else None,
            "latest": max(dates) if dates else None
        },
        "competitors": competitors,
        "categories": categories
    }

@app.get("/api/competitor-pricing")
async def get_competitor_pricing(
    competitor: Optional[str] = Query(None, description="Filter by competitor name"),
    category: Optional[str] = Query(None, description="Filter by product category"),
    date: Optional[str] = Query(None, description="Filter by scrape date (YYYY-MM-DD)"),
    price_index_min: Optional[float] = Query(None, description="Minimum price index"),
    price_index_max: Optional[float] = Query(None, description="Maximum price index"),
    limit: int = Query(100, ge=1, le=1000, description="Number of records to return"),
    offset: int = Query(0, ge=0, description="Number of records to skip")
):
    """
    Get competitor pricing data with filtering and pagination
    """
    try:
        filtered_data = data_manager.competitor_data
        
        # Apply filters
        if competitor:
            filtered_data = [item for item in filtered_data 
                           if competitor.lower() in item.get('competitor_name', '').lower()]
        
        if category:
            filtered_data = [item for item in filtered_data 
                           if category.lower() == item.get('product_category', '').lower()]
        
        if date:
            filtered_data = [item for item in filtered_data 
                           if item.get('scrape_date') == date]
        
        if price_index_min is not None:
            filtered_data = [item for item in filtered_data 
                           if item.get('overall_price_index', 0) >= price_index_min]
        
        if price_index_max is not None:
            filtered_data = [item for item in filtered_data 
                           if item.get('overall_price_index', 0) <= price_index_max]
        
        # Paginate results
        total_records = len(filtered_data)
        paginated_data = filtered_data[offset:offset + limit]
        
        return {
            "success": True,
            "data": paginated_data,
            "pagination": {
                "total": total_records,
                "limit": limit,
                "offset": offset,
                "returned": len(paginated_data),
                "has_more": (offset + limit) < total_records
            },
            "filters_applied": {
                "competitor": competitor,
                "category": category,
                "date": date,
                "price_index_range": f"{price_index_min}-{price_index_max}" if price_index_min or price_index_max else None
            }
        }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing request: {str(e)}")

@app.get("/api/competitor-pricing/summary")
async def get_competitor_summary(
    date: Optional[str] = Query(None, description="Filter by specific date"),
    category: Optional[str] = Query(None, description="Filter by category")
):
    """
    Get summary statistics for competitor pricing
    """
    try:
        filtered_data = data_manager.competitor_data
        
        if date:
            filtered_data = [item for item in filtered_data if item.get('scrape_date') == date]
        
        if category:
            filtered_data = [item for item in filtered_data if item.get('product_category') == category]
        
        competitor_summary = {}
        category_summary = {}
        
        for item in filtered_data:
            competitor = item['competitor_name']
            product_category = item['product_category']
            
            # Competitor summary
            if competitor not in competitor_summary:
                competitor_summary[competitor] = {
                    "competitor_name": competitor,
                    "total_categories": 0,
                    "total_price_index": 0,
                    "total_products": 0,
                    "categories_covered": []
                }
            
            competitor_summary[competitor]["total_categories"] += 1
            competitor_summary[competitor]["total_price_index"] += item["overall_price_index"]
            competitor_summary[competitor]["total_products"] += len(item.get("products_monitored", []))
            if product_category not in competitor_summary[competitor]["categories_covered"]:
                competitor_summary[competitor]["categories_covered"].append(product_category)
            
            # Category summary
            if product_category not in category_summary:
                category_summary[product_category] = {
                    "category_name": product_category,
                    "total_competitors": 0,
                    "total_price_index": 0,
                    "total_products": 0
                }
            
            category_summary[product_category]["total_competitors"] += 1
            category_summary[product_category]["total_price_index"] += item["overall_price_index"]
            category_summary[product_category]["total_products"] += len(item.get("products_monitored", []))
        
        # Calculate averages
        for competitor in competitor_summary.values():
            if competitor["total_categories"] > 0:
                competitor["average_price_index"] = round(
                    competitor["total_price_index"] / competitor["total_categories"], 3
                )
            competitor["categories_covered"] = sorted(competitor["categories_covered"])
            del competitor["total_price_index"]  # Remove temporary field
        
        for category in category_summary.values():
            if category["total_competitors"] > 0:
                category["average_price_index"] = round(
                    category["total_price_index"] / category["total_competitors"], 3
                )
            del category["total_price_index"]  # Remove temporary field
        
        return {
            "success": True,
            "summary": {
                "total_records": len(filtered_data),
                "total_competitors": len(competitor_summary),
                "total_categories": len(category_summary),
                "date_filter": date,
                "category_filter": category
            },
            "competitors": list(competitor_summary.values()),
            "categories": list(category_summary.values())
        }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error generating summary: {str(e)}")

@app.get("/api/competitor-pricing/competitors")
async def get_competitors():
    """Get list of all unique competitors"""
    try:
        competitors = data_manager.get_competitors()
        return {
            "success": True,
            "competitors": competitors,
            "count": len(competitors)
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error retrieving competitors: {str(e)}")

@app.get("/api/competitor-pricing/categories")
async def get_categories():
    """Get list of all unique product categories"""
    try:
        categories = data_manager.get_categories()
        return {
            "success": True,
            "categories": categories,
            "count": len(categories)
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error retrieving categories: {str(e)}")

@app.get("/api/competitor-pricing/dates")
async def get_dates():
    """Get list of all unique scrape dates"""
    try:
        dates = data_manager.get_dates()
        return {
            "success": True,
            "dates": dates,
            "count": len(dates)
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error retrieving dates: {str(e)}")

@app.post("/api/competitor-pricing/reload")
async def reload_data():
    """Reload competitor data from source file"""
    try:
        result = data_manager.reload_data()
        return {
            "success": True,
            "message": result["message"],
            "records_loaded": result["records"],
            "source_file": result["source_file"],
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error reloading data: {str(e)}")

@app.get("/api/competitor-pricing/{competitor_id}")
async def get_competitor_by_id(competitor_id: str):
    """Get competitor data by competitor ID"""
    try:
        competitor_data = [item for item in data_manager.competitor_data 
                         if item.get('competitor_id') == competitor_id]
        
        if not competitor_data:
            raise HTTPException(status_code=404, detail=f"Competitor with ID {competitor_id} not found")
        
        return {
            "success": True,
            "competitor_id": competitor_id,
            "data": competitor_data
        }
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error retrieving competitor data: {str(e)}")

# Error handlers
@app.exception_handler(404)
async def not_found_handler(request, exc):
    return JSONResponse(
        status_code=404,
        content={"success": False, "error": "Endpoint not found", "path": request.url.path}
    )

@app.exception_handler(500)
async def internal_error_handler(request, exc):
    return JSONResponse(
        status_code=500,
        content={"success": False, "error": "Internal server error"}
    )

if __name__ == "__main__":
    print("🚀 Starting MegaMart Competitor Intelligence API...")
    print("📊 Available endpoints:")
    print("   http://localhost:8000/docs - Interactive API documentation")
    print("   http://localhost:8000/redoc - Alternative documentation")
    print("   http://localhost:8000/api/health - Health check")
    print("   http://localhost:8000/api/stats - API statistics")
    
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )