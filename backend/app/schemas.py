from pydantic import BaseModel


class RegisterIn(BaseModel):
    company_name: str
    email: str
    password: str


class TokenOut(BaseModel):
    access_token: str
    token_type: str = "bearer"


class WarehouseIn(BaseModel):
    name: str
    lat: float
    lng: float


class WarehouseOut(WarehouseIn):
    id: int

    class Config:
        from_attributes = True


class RouteIn(BaseModel):
    origin_id: int
    destination_id: int
    transport_mode: str
    load_tons: float = 10


class RouteOut(BaseModel):
    id: int
    origin_id: int
    destination_id: int
    origin_name: str
    destination_name: str
    origin_lat: float
    origin_lng: float
    dest_lat: float
    dest_lng: float
    transport_mode: str
    load_tons: float
    distance_km: float
    emissions_kg: float
