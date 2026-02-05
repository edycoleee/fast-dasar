"""
SQLAlchemy Database Setup dan Models
Week 2a: CRUD dengan SQLAlchemy ORM
"""

from sqlalchemy import create_engine, Column, Integer, String
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

# Database URL untuk SQLite
# Format: sqlite:///./nama_database.db
DATABASE_URL = "sqlite:///./siswa_orm.db"

# Create engine
# connect_args={"check_same_thread": False} hanya untuk SQLite
engine = create_engine(
    DATABASE_URL,
    connect_args={"check_same_thread": False}
)

# SessionLocal class untuk membuat database sessions
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Base class untuk models
Base = declarative_base()


# ==================== MODELS ====================

class Siswa(Base):
    """
    SQLAlchemy Model untuk tabel siswa
    
    Equivalent dengan:
    CREATE TABLE siswa (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        nama VARCHAR(100) NOT NULL,
        email VARCHAR(100) NOT NULL UNIQUE
    )
    """
    __tablename__ = "siswa"
    
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    nama = Column(String(100), nullable=False)
    email = Column(String(100), unique=True, nullable=False, index=True)
    
    def __repr__(self):
        return f"<Siswa(id={self.id}, nama='{self.nama}', email='{self.email}')>"


# ==================== DATABASE FUNCTIONS ====================

def init_db():
    """
    Inisialisasi database - create semua tables
    Equivalent dengan: CREATE TABLE IF NOT EXISTS siswa (...)
    """
    Base.metadata.create_all(bind=engine)
    print("✅ Database initialized with SQLAlchemy ORM")


def get_db():
    """
    Dependency untuk mendapatkan database session
    Akan di-inject ke FastAPI endpoints dengan Depends()
    
    Usage:
        @app.get("/api/siswa/")
        def read_siswa(db: Session = Depends(get_db)):
            siswa = db.query(Siswa).all()
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
