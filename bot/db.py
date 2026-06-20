import os
from sqlalchemy import Column, Integer, String, BigInteger, create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///runekeeper.db")

Base = declarative_base()

class UserProfile(Base):
    __tablename__ = "user_profiles"
    id = Column(Integer, primary_key=True)
    discord_id = Column(BigInteger, index=True, nullable=False)
    guild_id = Column(BigInteger, index=True, nullable=False)
    balance = Column(Integer, default=0)
    xp = Column(Integer, default=0)
    level = Column(Integer, default=0)
    brawlhalla_handle = Column(String, nullable=True)

engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False} if DATABASE_URL.startswith("sqlite") else {})
SessionLocal = sessionmaker(bind=engine)

def init_db():
    Base.metadata.create_all(bind=engine)
