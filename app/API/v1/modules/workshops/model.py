from sqlalchemy import Column, Integer, String
from sqlalchemy.sql.schema import ForeignKey
from sqlalchemy.orm import relationship

from app.database.base_class import Base, TimestampMixin, SoftDeleteMixin

class WorkshopType(Base, TimestampMixin):
    __tablename__ = "workshop_types"
    id = Column(Integer, primary_key=True)
    name = Column(String(60), nullable=False)

    workshop = relationship("Workshop", back_populates="type", uselist=False, lazy="joined")


class Workshop(Base, SoftDeleteMixin, TimestampMixin):
    __tablename__ = "workshops"
    id = Column(Integer, primary_key=True)
    name = Column(String(80), nullable=False)
    name_short = Column(String(30), nullable=False)
    rut = Column(String(20), nullable=True, default='')
    region_id = Column(Integer, ForeignKey("regions.id"), nullable=False, server_default='16') #RM
    commune_id = Column(Integer, ForeignKey("communes.id"), nullable=False, server_default='269') #STGO
    address = Column(String(100), nullable=True, default='')
    phone = Column(String(60), nullable=True, default='')
    email = Column(String(60), nullable=True, default='')
    type_id = Column(Integer, ForeignKey("workshop_types.id"), nullable=True) #TYPE_WORKSHOP

    region = relationship("Region", back_populates="workshop", uselist=False, lazy="joined")
    commune = relationship("Commune", back_populates="workshop", uselist=False, lazy="joined")
    type = relationship("WorkshopType", back_populates="workshop", uselist=False, lazy="joined")
    user = relationship("User", back_populates="workshop", uselist=False)


    
    
