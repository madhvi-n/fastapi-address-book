from sqlalchemy import create_engine, Column, Integer, String, Float
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from geopy import distance

SQLALCHEMY_DATABASE_URL = "sqlite:///../addressbook.sqlite3"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False}
)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

class AddressTable(Base):
    __tablename__ = "addresses"

    id = Column(Integer, primary_key=True, index=True)
    street = Column(String)
    city = Column(String)
    state = Column(String)
    zip_code = Column(String)
    latitude = Column(Float, index=True)
    longitude = Column(Float, index=True)

    def distance_to(self, lat, lon):
            return distance.distance((self.latitude, self.longitude), (lat, lon)).miles

Base.metadata.create_all(bind=engine)
