from sqlalchemy import Column, Integer, String, Boolean
from sqlalchemy.sql.schema import ForeignKey
from sqlalchemy.orm import relationship

from app.database.base_class import Base, TimestampMixin, SoftDeleteMixin



class NotificationType(Base, SoftDeleteMixin, TimestampMixin):
    __tablename__ = "notification_types"
    id = Column(Integer, primary_key=True)
    name = Column(String(100), nullable=False) #SYSTEM_ALERT, REMINDER, STATUS_CHANGE

    notifications = relationship("Notification", back_populates="notification_type", uselist=True)

class SeenBy(Base, SoftDeleteMixin, TimestampMixin):
    __tablename__ = "seen_by"
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    notification_id = Column(Integer, ForeignKey("notifications.id"), nullable=False)

    notification = relationship("Notification", back_populates="seen_by", uselist=False)

class Notification(Base, SoftDeleteMixin, TimestampMixin):
    __tablename__ = "notifications"
    
    id = Column(Integer, primary_key=True)

    # Usuario que gatilla la notificación (opcional)
    triggered_by_user_id = Column(Integer, ForeignKey("users.id"), nullable=True, default=None)
    
    # Usuario que recibe la notificación (opcional)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=True, default=None)
    
    # Relación con la tabla de roles (opcional)
    role_id = Column(Integer, ForeignKey("roles.id"), nullable=True, default=None)

    workshop_id = Column(Integer, ForeignKey("workshops.id"), nullable=True, default=None)

    case_id = Column(Integer, ForeignKey("cases.id"), nullable=True, default=None)

    quote_id = Column(Integer, ForeignKey("quotes_cases.id"), nullable=True, default=None)

    type_id = Column(Integer, ForeignKey("notification_types.id"), nullable=False)

    # Mensaje de la notificación
    message = Column(String(500), nullable=False)
    
    # Módulo o contexto al que pertenece la notificación
    module = Column(String(500), nullable=True, default=None)
    
    # Indica si la notificación ha sido leída
    is_read = Column(Boolean, nullable=False, default=False)

    notification_type = relationship("NotificationType", back_populates="notifications", uselist=False)

    seen_by = relationship("SeenBy", back_populates="notification", lazy='joined')
    

    
    
    
    



    
