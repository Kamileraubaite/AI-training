from fastapi import FastAPI

# Create the API application.
app = FastAPI(title="Banking Complaints Intelligence API")


# Check that the API is running.
@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}