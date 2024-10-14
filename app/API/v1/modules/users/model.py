from sqlalchemy import Column, Integer, String
from sqlalchemy.sql.schema import ForeignKey
from sqlalchemy.orm import relationship

from app.database.base_class import Base, TimestampMixin, SoftDeleteMixin
from ..workshops.model import Workshop


class AcceptedTerms(Base, SoftDeleteMixin, TimestampMixin):
    __tablename__ = "accepted_terms"
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    description = Column(String(500), nullable=False)

class Role(Base, SoftDeleteMixin, TimestampMixin):
    __tablename__ = "roles"
    id = Column(Integer, primary_key=True)
    name = Column(String(60), nullable=False, unique=True)

    # One-to-one relationship with User
    user = relationship("User", back_populates="role", uselist=False)

class User(Base, SoftDeleteMixin, TimestampMixin):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True)
    name = Column(String(60), nullable=False)
    last_name = Column(String(60), nullable=False, default='')
    email = Column(String(60), nullable=False, unique=True)
    phone = Column(String(60), nullable=False)
    password = Column(String(100), nullable=False)

    role_id = Column(Integer, ForeignKey("roles.id"), nullable=False)
    workshop_id = Column(Integer, ForeignKey("workshops.id"), nullable=True)

    # One-to-one relationship with Role
    role = relationship("Role", back_populates="user")

    case = relationship("Case", back_populates="user" , uselist=False)
    quote = relationship("QuoteCase", back_populates="user" , uselist=False)
    workshop = relationship("Workshop", back_populates="user" , uselist=False, lazy="joined")
    quote_cases = relationship('QuoteCase', back_populates='user')
    
   
    # Backref for AwardedQuoteCase as `workshop_user`
    """ workshop_awarded_quote_case = relationship("AwardedQuoteCase", foreign_keys=[AwardedQuoteCase.workshop_user_id], back_populates="workshop_user", uselist=False) """


    
