import httpx
from fastapi import FastAPI, Request, Response
from middleware import add_custom_middleware

app = FastAPI()

add_custom_middleware(app)

client = httpx.AsyncClient(base_url="http://localhost:8001")

@app.api_route("/{path:path}", methods=["GET", "POST", "PUT", "DELETE", "PATCH", "OPTIONS"])
async def proxy(request: Request, path: str):
    query = str(request.url.query)
    url = f"{path}?{query}" if query else path
    # Forward the request
    headers = dict(request.headers)
    # Remove host header to avoid issues
    headers.pop("host", None)
    response = await client.request(
        method=request.method,
        url=url,
        headers=headers,
        content=await request.body(),
    )
    return Response(content=response.content, status_code=response.status_code, headers=dict(response.headers))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="localhost", port=8000)