from sqlalchemy import Column, Integer, String
from sqlalchemy.sql.schema import ForeignKey
from sqlalchemy.orm import relationship

from app.database.base_class import Base, TimestampMixin, SoftDeleteMixin

class Brand(Base, SoftDeleteMixin, TimestampMixin):
    __tablename__ = "brands"
    id = Column(Integer, primary_key=True)
    name = Column(String(200), nullable=False)

    models = relationship("Model", back_populates="brand")

    car = relationship("CarCase", back_populates="brand", uselist=False)

class Model(Base, SoftDeleteMixin, TimestampMixin):
    __tablename__ = "models"
    id = Column(Integer, primary_key=True)
    name = Column(String(200), nullable=False)
    brand_id = Column(Integer, ForeignKey("brands.id"), nullable=False)
    start_year_range = Column(Integer, nullable=False)
    end_year_range = Column(Integer, nullable=False)

    brand = relationship("Brand", back_populates="models")

    car = relationship("CarCase", back_populates="model", uselist=False)

    
