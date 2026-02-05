"""
User Model
SQLAlchemy model for users/siswa
"""

from sqlalchemy import Column, Integer, String

from app.db.base import Base


class User(Base):
    """
    User model (Siswa)
    
    Attributes:
        id: Primary key
        nama: User name
        email: Unique email address
        password: Hashed password
        role: User role (admin/user)
    """
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    nama = Column(String(100), nullable=False)
    email = Column(String(100), unique=True, nullable=False, index=True)
    password = Column(String(255), nullable=False)
    role = Column(String(20), nullable=False, default="user")
    
    def __repr__(self):
        return f"<User(id={self.id}, nama='{self.nama}', email='{self.email}', role='{self.role}')>"
