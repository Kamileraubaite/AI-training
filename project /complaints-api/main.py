from fastapi import FastAPI

from routers import customers, products, complaints

# Create the API application.
app = FastAPI(title="Banking Complaints Intelligence API")

app.include_router(customers.router)
app.include_router(products.router)
app.include_router(complaints.router)

# Check that the API is running.
@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}