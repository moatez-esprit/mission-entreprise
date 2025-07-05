from sqlalchemy import Column, Integer, String, Text, Float
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

class CV(Base):
    __tablename__ = "cvs"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    text = Column(Text, nullable=False)

class JobDescription(Base):
    __tablename__ = "jobs"
    id = Column(Integer, primary_key=True, index=True)
    description = Column(Text, nullable=False)
