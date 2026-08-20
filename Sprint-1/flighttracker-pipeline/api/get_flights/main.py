import os
from fastapi import FastAPI, Query
from typing import Optional
import uvicorn
from repository import FirestoreFlightRepository, FlightRepository

app = FastAPI(title="FlightTracker API", description="API para consultar vuelos procesados")

# Cassandra will replace this adapter without changing the HTTP contract.
repository: FlightRepository = FirestoreFlightRepository()

@app.get("/flights")
async def get_flights(
    airline: Optional[str] = Query(None, description="Código IATA de la aerolínea (ej. AA)"),
    date: Optional[str] = Query(None, description="Fecha en formato YYYY-MM-DD"),
    limit: int = Query(100, description="Número máximo de resultados")
):
    """
    Endpoint para consultar vuelos filtrados por aerolínea y/o fecha.
    """
    try:
        results = repository.list_flights(airline, date, limit)
        return {"status": "success", "count": len(results), "data": results}
    except Exception as e:
        return {"status": "error", "message": str(e)}

@app.get("/health")
async def health():
    return {"status": "healthy"}

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=int(os.getenv("PORT", 8080)))
