from datetime import datetime
from sqlalchemy import Column, Integer, String, Float, ForeignKey, DateTime, JSON
from sqlalchemy.orm import relationship
from .database import Base


class Company(Base):
    __tablename__ = "companies"
    id = Column(Integer, primary_key=True)
    name = Column(String, unique=True, nullable=False)


class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True)
    company_id = Column(Integer, ForeignKey("companies.id"), nullable=False)
    email = Column(String, unique=True, nullable=False)
    password_hash = Column(String, nullable=False)
    role = Column(String, default="manager")


class Warehouse(Base):
    __tablename__ = "warehouses"
    id = Column(Integer, primary_key=True)
    company_id = Column(Integer, ForeignKey("companies.id"), nullable=False)
    name = Column(String, nullable=False)
    lat = Column(Float, nullable=False)
    lng = Column(Float, nullable=False)


class Route(Base):
    __tablename__ = "routes"
    id = Column(Integer, primary_key=True)
    company_id = Column(Integer, ForeignKey("companies.id"), nullable=False)
    origin_id = Column(Integer, ForeignKey("warehouses.id"), nullable=False)
    destination_id = Column(Integer, ForeignKey("warehouses.id"), nullable=False)
    transport_mode = Column(String, nullable=False)  # truck | rail | ship | air
    load_tons = Column(Float, default=10)
    origin = relationship("Warehouse", foreign_keys=[origin_id])
    destination = relationship("Warehouse", foreign_keys=[destination_id])


class WeatherSnapshot(Base):
    __tablename__ = "weather_snapshots"
    id = Column(Integer, primary_key=True)
    warehouse_id = Column(Integer, ForeignKey("warehouses.id"), nullable=False)
    fetched_at = Column(DateTime, default=datetime.utcnow)
    wind_speed = Column(Float)      # km/h on the peak-risk day
    precipitation = Column(Float)   # mm on the peak-risk day
    temp = Column(Float)            # max temp C on the peak-risk day
    risk_score = Column(Float)      # peak risk over the 7-day forecast (0-100)
    peak_day = Column(String)
    forecast = Column(JSON)         # [{date, risk, wind, rain, temp}, ...]
