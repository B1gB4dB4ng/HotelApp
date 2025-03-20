from db.database import Base
from sqlalchemy import DECIMAL, Column, Integer, String, Boolean


class Dbuser(Base):
    __tablename__ = "user"

    id = Column(Integer, primary_key=True, index=True)
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


class Dbhotel(Base):
    __tablename__ = "hotel"
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, index=True)
    description = Column(String, nullable=True)
    owner_username = Column(String, nullable=False)  # This is the new column
    img_link = Column(String, nullable=True)
    is_active = Column(Boolean, default=True)
    price = Column(DECIMAL(8, 2), nullable=False)
    location = Column(String, nullable=False)
