from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
import uvicorn

from config import settings
from app.database import init_db
from app.api.v1 import auth, vehicles, bookings, payments, kyc, contracts, loyalty, reviews


@asynccontextmanager
async def lifespan(app: FastAPI):
   # Startup
   await init_db()
   yield
   # Shutdown
   pass


app = FastAPI(
   title="Hiyacars Rental API",
   description="Backend API for car rental platform",
   version="1.0.0",
   lifespan=lifespan
)

# CORS Middleware
app.add_middleware(
   CORSMiddleware,
   allow_origins=settings.cors_origins_list,
   allow_credentials=True,
   allow_methods=["*"],
   allow_headers=["*"],
)

# Health check
@app.get("/health")
async def health_check():
   return {"status": "healthy", "environment": settings.ENVIRONMENT}

# API Routes - Using Supabase Auth
app.include_router(auth.router, prefix="/api/v1/auth", tags=["Authentication"])
app.include_router(vehicles.router, prefix="/api/v1/vehicles", tags=["Vehicles"])
app.include_router(bookings.router, prefix="/api/v1/bookings", tags=["Bookings"])
app.include_router(payments.router, prefix="/api/v1/payments", tags=["Payments"])
app.include_router(kyc.router, prefix="/api/v1/kyc", tags=["KYC"])
app.include_router(contracts.router, prefix="/api/v1/contracts", tags=["Contracts"])
app.include_router(loyalty.router, prefix="/api/v1/loyalty", tags=["Loyalty"])
app.include_router(reviews.router, prefix="/api/v1/reviews", tags=["Reviews"])


if __name__ == "__main__":
   uvicorn.run(
       "main:app",
       host="0.0.0.0",
       port=8000,
       reload=settings.DEBUG
   )



