from db.database import Base
from sqlalchemy import DECIMAL, Column, Enum, Integer, String, Boolean, ForeignKey
from sqlalchemy.orm import relationship
from enum import Enum as PyEnum


# ========== USER MODEL ==========
class Dbuser(Base):
    __tablename__ = "user"
    id = Column(Integer, primary_key=True, index=True)
    # One-to-many: One user has many hotels
    hotels = relationship("Dbhotel", back_populates="owner")
    username = Column(String, unique=True)
    email = Column(String, unique=True)
    hashed_password = Column(String)
    is_superuser = Column(Boolean, default=False)


# ========== HOTEL MODEL ==========


class IsActive(PyEnum):  # Define Enum for strict values
    INACTIVE = "inactive"
    ACTIVE = "active"
    DELETED = "deleted"


class Dbhotel(Base):
    __tablename__ = "hotel"

    id = Column(Integer, primary_key=True, index=True)
    # ForeignKey to DbUser
    owner_id = Column(Integer, ForeignKey("user.id"))
    # Many-to-one: Many hotels belong to one user
    owner = relationship("Dbuser", back_populates="hotels")
    name = Column(String, index=True)
    location = Column(String, nullable=False)
    description = Column(String, nullable=True)
    price = Column(DECIMAL(8, 2), nullable=False)
    is_active = Column(
        Enum(IsActive), nullable=False, default=IsActive.ACTIVE
    )  # Enforced Enum
    img_link = Column(String, nullable=True)
    is_approved = Column(Boolean, default=False)
