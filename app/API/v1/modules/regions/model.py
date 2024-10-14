from sqlalchemy import Column, Integer, String
from sqlalchemy.sql.schema import ForeignKey
from sqlalchemy.orm import relationship

from app.database.base_class import Base, TimestampMixin, SoftDeleteMixin

class Region(Base, SoftDeleteMixin, TimestampMixin):
    __tablename__ = "regions"
    id = Column(Integer, primary_key=True)
    name = Column(String(200), nullable=False, unique=True)

    # Relación uno a muchos con las comunas
    communes = relationship("Commune", back_populates="region")
    workshop = relationship("Workshop", back_populates="region", uselist=False)

    

class Commune(Base, SoftDeleteMixin, TimestampMixin):
    __tablename__ = "communes"
    id = Column(Integer, primary_key=True)
    name = Column(String(200), nullable=False, unique=True)
    region_id = Column(Integer, ForeignKey("regions.id"), nullable=False)

    # Relación muchos a uno con la región
    region = relationship("Region", back_populates="communes")
    workshop = relationship("Workshop", back_populates="commune", uselist=False)

    
