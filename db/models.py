from db.database import Base
from sqlalchemy import DECIMAL, Column, Enum, Integer, String, Boolean, ForeignKey, Date
from sqlalchemy.orm import relationship
from enum import Enum as PyEnum


# ========== USER MODEL ==========
class Dbuser(Base):
    __tablename__ = "user"
    id = Column(Integer, primary_key=True, index=True)
    # One-to-many: One user has many hotels
    hotels = relationship("Dbhotel", back_populates="owner")
    # One-to-many: one user has many booking
    bookings = relationship("Dbbooking", back_populates="user")
    username = Column(String, unique=True)
    email = Column(String, unique=True)
    hashed_password = Column(String)
    is_superuser = Column(Boolean, default=False)


# ========== HOTEL MODEL ==========


class IsActive(PyEnum):  # Define Enum for strict values
    inactive = "inactive"
    active = "active"
    deleted = "deleted"


class Dbhotel(Base):
    __tablename__ = "hotel"

    id = Column(Integer, primary_key=True, index=True)
    # ForeignKey to DbUser
    owner_id = Column(Integer, ForeignKey("user.id"))
    # Many-to-one: Many hotels belong to one user
    owner = relationship("Dbuser", back_populates="hotels")
    #
    bookings = relationship("Dbbooking", back_populates="hotel")
    # One-to-many: Hotel can have several rooms
    rooms = relationship("Dbroom", back_populates="hotel")
    name = Column(String, index=True)
    location = Column(String, nullable=False)
    description = Column(String, nullable=True)
    price = Column(DECIMAL(8, 2), nullable=False)
    is_active = Column(
        Enum(IsActive), nullable=False, default=IsActive.active
    )  # Enforced Enum
    img_link = Column(String, nullable=True)
    is_approved = Column(Boolean, default=False)


# ========== ROOM MODEL ===========

class Dbroom(Base):
    __tablename__ = "room"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    description = Column(String, nullable=True)
    price = Column(DECIMAL(8, 2), nullable=False)
    # ForeignKey to Dbhotel
    hotel_id = Column(Integer, ForeignKey("hotel.id"))
    #Many-to-one: Many rooms belong to hotel
    hotel = relationship("Dbhotel", back_populates="rooms")
    img_link = Column(String, nullable=True)

# ========== BOOKING MODEL ==========


class Dbbooking(Base):
    __tablename__ = "booking"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("user.id"))
    hotel_id = Column(Integer, ForeignKey("hotel.id"))
    check_in_date = Column(Date, nullable=False)
    check_out_date = Column(Date, nullable=False)
    is_active = Column(Enum(IsActive), nullable=False, default=IsActive.active)
    # Relationships back to user and hotel
    user = relationship("Dbuser", back_populates="bookings")
    hotel = relationship("Dbhotel", back_populates="bookings")
