import logging
import time
from datetime import datetime
from fastapi import FastAPI, Request, Response, HTTPException
from fastapi.responses import RedirectResponse, HTMLResponse
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
import httpx
import os

# Set up standard logging to print to console
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s")
logger = logging.getLogger("api-gateway")

app = FastAPI(title="SAD Project API Gateway", description="An Intelligent Gateway acting as a single entry point.")

# Make sure static directory exists
os.makedirs("static/css", exist_ok=True)
app.mount("/static", StaticFiles(directory="static"), name="static")

# Templates location
templates = Jinja2Templates(directory="templates")

# Dashboard state mocked
app.state.total_requests = 1342
recent_requests = [
    {"method": "GET", "path": "/customer/api/users", "status": 200, "time": "10:23:45 AM", "duration": "12ms"},
    {"method": "POST", "path": "/laptop/api/orders", "status": 201, "time": "10:24:00 AM", "duration": "30ms"},
    {"method": "GET", "path": "/chatbot/session", "status": 200, "time": "10:25:21 AM", "duration": "45ms"}
]

# Define Service routing URLs
SERVICES = {
    "customer": "http://customer-service:8000",
    "chatbot":  "http://chatbot-service:8000",
    "staff":    "http://staff-service:8000",
    "laptop":   "http://laptop-service:8000",
    "mobile":   "http://mobile-service:8000",
}

# Use a globally managed httpx AsyncClient
client = httpx.AsyncClient()

@app.on_event("shutdown")
async def shutdown_event():
    await client.aclose()

@app.middleware("http")
async def gateway_middleware(request: Request, call_next):
    app.state.total_requests += 1
    start_time = time.time()
    
    # 1. Logging Capability (Gateway Feature)
    logger.info(f"Incoming Request: {request.method} {request.url.path}")

    # Process the actual request
    response = await call_next(request)

    # Calculate duration
    process_time = (time.time() - start_time) * 1000
    formatted_process_time = f"{process_time:.0f}ms"

    # Log response status
    logger.info(f"Response Status: {response.status_code} in {formatted_process_time}")
    
    # Update dashboard logic (only log API proxy requests, ignore static/favicon)
    if "static" not in request.url.path and "favicon" not in request.url.path and request.url.path != "/":
        recent_requests.insert(0, {
            "method": request.method, 
            "path": request.url.path, 
            "status": response.status_code, 
            "time": datetime.now().strftime("%I:%M:%S %p"),
            "duration": formatted_process_time
        })
        if len(recent_requests) > 8:
            recent_requests.pop()
    
    # 3. Adding Gateway headers
    response.headers["X-Gateway-Processed"] = "FastAPI-Powered"

    return response


@app.get("/", response_class=HTMLResponse)
async def root(request: Request):
    return templates.TemplateResponse("dashboard.html", {
        "request": request, 
        "services": SERVICES.keys(), 
        "services_config": SERVICES,
        "recent_requests": recent_requests,
        "total_requests": getattr(app.state, "total_requests", 1342)
    })

# --- Service Proxies ---

async def proxy_request(service_url: str, path: str, request: Request):
    """Generic function to proxy requests to target microservices."""
    url = f"{service_url}/{path}"
    
    # Prepare proxy headers, passing along necessary client headers
    headers = dict(request.headers)
    headers.pop("host", None) # Remove original host header to let httpx determine it
    
    try:
        # Stream the request directly to the backend
        req = client.build_request(
            method=request.method,
            url=url,
            headers=headers,
            content=await request.body()
        )
        resp = await client.send(req, stream=True)
        
        # Build the FastAPI response, streaming the body back
        # Exclude headers that can mess up chunking/encoding
        excluded_headers = {'content-encoding', 'content-length', 'transfer-encoding', 'connection'}
        proxy_headers = {
            kv[0].decode(): kv[1].decode() for kv in resp.headers.raw
            if kv[0].decode().lower() not in excluded_headers
        }
        
        async def response_stream():
            async for chunk in resp.aiter_bytes():
                yield chunk

        return Response(
            content=await resp.aread(), # For simple implementation, read it fully. If large files, use StreamingResponse.
            status_code=resp.status_code,
            headers=proxy_headers
        )
    except httpx.ConnectError:
        logger.error(f"Failed to connect to backend service at {service_url}")
        raise HTTPException(status_code=502, detail="Bad Gateway: Target service is down")


# --- Routing Rules ---

@app.api_route("/customer/{path:path}", methods=["GET", "POST", "PUT", "DELETE", "PATCH", "OPTIONS", "HEAD"])
async def route_customer(path: str, request: Request):
    # Appends customer/ prefix exactly like proxy_pass http://customer-service:8000/;
    # NGINX syntax with trailing slash replaces the matched portion. 
    # But for Django forcescript URL, it might expect the prefix.
    # NGINX original: location /customer/ { proxy_pass http://customer-service:8000/; }
    # Let's pass the raw path.
    return await proxy_request(SERVICES["customer"], path, request)

@app.api_route("/chatbot/{path:path}", methods=["GET", "POST", "PUT", "DELETE", "PATCH", "OPTIONS", "HEAD"])
async def route_chatbot(path: str, request: Request):
    return await proxy_request(SERVICES["chatbot"], path, request)

@app.api_route("/staff/{path:path}", methods=["GET", "POST", "PUT", "DELETE", "PATCH", "OPTIONS", "HEAD"])
async def route_staff(path: str, request: Request):
    return await proxy_request(SERVICES["staff"], path, request)

@app.api_route("/laptop/{path:path}", methods=["GET", "POST", "PUT", "DELETE", "PATCH", "OPTIONS", "HEAD"])
async def route_laptop(path: str, request: Request):
    return await proxy_request(SERVICES["laptop"], path, request)

@app.api_route("/mobile/{path:path}", methods=["GET", "POST", "PUT", "DELETE", "PATCH", "OPTIONS", "HEAD"])
async def route_mobile(path: str, request: Request):
    return await proxy_request(SERVICES["mobile"], path, request)

# --- Specific API routes from Nginx config ---

@app.api_route("/api/laptops/{path:path}", methods=["GET", "POST", "PUT", "DELETE", "PATCH", "OPTIONS", "HEAD"])
async def route_api_laptops(path: str, request: Request):
    full_path = f"api/laptops/{path}" if path else "api/laptops/"
    return await proxy_request(SERVICES["laptop"], full_path, request)

@app.get("/api/laptop")
@app.get("/api/laptop/")
async def redirect_api_laptop():
    return RedirectResponse(url="/api/laptops/")

@app.api_route("/api/mobiles/{path:path}", methods=["GET", "POST", "PUT", "DELETE", "PATCH", "OPTIONS", "HEAD"])
async def route_api_mobiles(path: str, request: Request):
    full_path = f"api/mobiles/{path}" if path else "api/mobiles/"
    return await proxy_request(SERVICES["mobile"], full_path, request)

@app.get("/api/mobile")
@app.get("/api/mobile/")
async def redirect_api_mobile():
    return RedirectResponse(url="/api/mobiles/")

