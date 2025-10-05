from sqlalchemy import Column, Integer, String, Float, DateTime
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
import datetime, os

Base = declarative_base()

class Reading(Base):
    __tablename__ = 'readings'
    id = Column(Integer, primary_key=True)
    timestamp = Column(DateTime, default=datetime.datetime.utcnow)
    operator = Column(String(100))
    plant = Column(String(100))
    ncu = Column(String(100))
    tcu_mac = Column(String(100))
    latitude = Column(Float)
    longitude = Column(Float)

def init_db(db_path='sqlite:///data/tcu.db'):
    os.makedirs('data', exist_ok=True)
    engine = create_engine(db_path, connect_args={"check_same_thread": False})
    Base.metadata.create_all(engine)
    Session = sessionmaker(bind=engine)
    return Session
