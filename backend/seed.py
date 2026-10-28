"""Run once:  python seed.py   (resets all tables and loads two demo companies)"""
from app.database import Base, engine, SessionLocal
from app.models import Company, User, Warehouse, Route, WeatherSnapshot
from app.auth import hash_password
from app.services.risk import fetch_forecast

DATA = {
    "Southern Freight Co": ("manager@southern.com", [
        ("Chennai Port", 13.0827, 80.2707), ("Coimbatore Hub", 11.0168, 76.9558),
        ("Mumbai Depot", 19.0760, 72.8777), ("Delhi Warehouse", 28.6139, 77.2090),
        ("Kolkata Port", 22.5726, 88.3639),
    ], [(0, 1, "truck", 12), (0, 2, "rail", 40), (2, 3, "truck", 15), (0, 4, "ship", 120)]),
    "Nordic Cargo Ltd": ("manager@nordic.com", [
        ("Rotterdam", 51.9244, 4.4777), ("Hamburg", 53.5511, 9.9937),
        ("Singapore Hub", 1.3521, 103.8198), ("Dubai Depot", 25.2048, 55.2708),
        ("Shanghai Port", 31.2304, 121.4737),
    ], [(0, 1, "truck", 20), (0, 3, "air", 2), (3, 2, "ship", 200), (2, 4, "ship", 150)]),
}

Base.metadata.drop_all(bind=engine)
Base.metadata.create_all(bind=engine)
db = SessionLocal()

for cname, (email, warehouses, routes) in DATA.items():
    c = Company(name=cname)
    db.add(c)
    db.flush()
    db.add(User(company_id=c.id, email=email, password_hash=hash_password("demo1234")))
    ws = []
    for name, lat, lng in warehouses:
        w = Warehouse(company_id=c.id, name=name, lat=lat, lng=lng)
        db.add(w)
        ws.append(w)
    db.flush()
    for o, d, mode, load in routes:
        db.add(Route(company_id=c.id, origin_id=ws[o].id, destination_id=ws[d].id, transport_mode=mode, load_tons=load))
    for w in ws:  # weather snapshots (skipped if offline)
        try:
            days = fetch_forecast(w.lat, w.lng)
            peak = max(days, key=lambda x: x["risk"])
            db.add(WeatherSnapshot(warehouse_id=w.id, wind_speed=peak["wind"], precipitation=peak["rain"],
                                   temp=peak["temp"], risk_score=peak["risk"], peak_day=peak["date"], forecast=days))
        except Exception:
            print("weather fetch failed for", w.name)

db.commit()
print("Seeded. Logins: manager@southern.com / manager@nordic.com  (password: demo1234)")
