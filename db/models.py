from db.database import Base
from sqlalchemy import DECIMAL, Column, Integer, String, Boolean, ForeignKey
from sqlalchemy.orm import relationship


# ========== USER MODEL ==========
class Dbuser(Base):
    __tablename__ = "user"
    id = Column(Integer, primary_key=True, index=True)
    #hotels = relationship("Dbhotel", back_populates="owner")
    username = Column(
        String,
        unique=True,
    )
    email = Column(
        String,
        unique=True,
    )
    hashed_password = Column(String)
    is_superuser = Column(Boolean, default=False)

# ========== HOTEL MODEL ==========
class Dbhotel(Base):
    __tablename__ = "hotel"

    id = Column(Integer, primary_key=True, index=True)
    #user_id = Column(Integer, ForeignKey("user.id"))  #ForeignKey to user table
    #owner = relationship("Dbuser", back_populates="hotels")  #Relationship to user

    name = Column(String, index=True)
    location = Column(String, nullable=False)
    description = Column(String, nullable=True)
    price = Column(DECIMAL(8, 2), nullable=False)
    is_active = Column(Boolean, default=True)
    img_link = Column(String, nullable=True)
    is_approved = Column(Boolean, default=False)

   