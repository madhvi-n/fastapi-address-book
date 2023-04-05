from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import JSONResponse
from database import SessionLocal, engine, AddressTable
from models import Address, AddressCreate
from sqlalchemy.orm import Session
from typing import List

address_router = APIRouter(prefix="/addresses")

def get_db():
    try:
        db = SessionLocal()
        yield db
    finally:
        db.close()


@address_router.get("/", response_model=List[Address])
def get_addresses(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    addresses = db.query(AddressTable).offset(skip).limit(limit).all()
    return addresses


@address_router.post("/create", response_model=Address)
def create_address(address: AddressCreate, db: Session = Depends(get_db)):
    db_address = AddressTable(**address.dict())
    db.add(db_address)
    db.commit()
    db.refresh(db_address)
    return db_address


@address_router.get("/{address_id}", response_model=Address)
def get_address(address_id: int, db: Session = Depends(get_db)):
    try:
        address_id = int(address_id)
    except ValueError:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid address ID provided")
    address = db.query(AddressTable).filter(AddressTable.id == address_id).first()
    if not address:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Address not found")
    return address


@address_router.put("/{address_id}", response_model=Address)
def update_address(address_id: int, address: AddressCreate, db: Session = Depends(get_db)):
    db_address = db.query(AddressTable).filter(AddressTable.id == address_id).first()
    if not db_address:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Address not found")
    for key, value in address.dict(exclude_unset=True).items():
        setattr(db_address, key, value)
    db.commit()
    db.refresh(db_address)
    return db_address


@address_router.delete("/{address_id}")
def delete_address(address_id: int, db: Session = Depends(get_db)):
    db_address = db.query(AddressTable).filter(AddressTable.id == address_id).first()
    if not db_address:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Address not found")
    db.delete(db_address)
    db.commit()
    return JSONResponse(content={"message": "Address deleted successfully"}, status_code=status.HTTP_200_OK)


@address_router.get("/nearby")
def get_nearby_addresses(latitude: float, longitude: float, distance: float = 1.0, db: Session = Depends(get_db)):
    # Get the address for the given latitude and longitude
    address = db.query(AddressTable).filter(AddressTable.latitude == latitude, AddressTable.longitude == longitude).first()
    if not address:
        return JSONResponse(content={"message": "Address not found"}, status_code=status.HTTP_404_NOT_FOUND)

    # Get the nearby addresses for the given address and distance
    addresses = db.query(AddressTable).filter(AddressTable.id != address.id).all()
    nearby_addresses = []
    for address in addresses:
        if address.distance_to(latitude, longitude) <= distance:
            nearby_addresses.append(address)
    if not nearby_addresses:
        return JSONResponse(content={"message": "No nearby addresses found"}, status_code=status.HTTP_404_NOT_FOUND)
    return JSONResponse(content={"addresses": nearby_addresses}, status_code=status.HTTP_200_OK)


@address_router.get("/nearby_from_address/{address}", response_model=List[Address])
def get_nearby_addresses(address: str, distance: float = 1.0, db: Session = Depends(get_db)):
    # Get the latitude and longitude of the address using a geocoding API
    geocode_result = requests.get(f"https://geocode.xyz/{address}", params={"json": 1}).json()
    if "error" in geocode_result:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid address")

    latitude = float(geocode_result["latt"])
    longitude = float(geocode_result["longt"])

    # Query the database for nearby addresses
    addresses = db.query(AddressTable).all()
    nearby_addresses = []
    for address in addresses:
        if address.distance_to(latitude, longitude) <= distance:
            nearby_addresses.append(address)

    if not nearby_addresses:
        return JSONResponse(content={"message": "No nearby addresses found"}, status_code=status.HTTP_404_NOT_FOUND)
    return JSONResponse(content={"addresses": nearby_addresses}, status_code=status.HTTP_200_OK)
