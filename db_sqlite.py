from sqlalchemy import create_engine, Column, Integer, String, Boolean, DateTime
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import datetime
from passlib.context import CryptContext

# Configuración del hash de contraseñas
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# Crear el motor de SQLite
SQLALCHEMY_DATABASE_URL = "sqlite:///./chat_app.db"
engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})

# Crear sesión
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Crear base declarativa
Base = declarative_base()

# Modelo de usuario
class User(Base):
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True)
    email = Column(String, unique=True, index=True)
    hashed_password = Column(String)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    
    @classmethod
    def get_by_username(cls, db, username):
        return db.query(cls).filter(cls.username == username).first()
    
    @classmethod
    def get_by_email(cls, db, email):
        return db.query(cls).filter(cls.email == email).first()
    
    @classmethod
    def create(cls, db, username, email, password):
        hashed_password = pwd_context.hash(password)
        user = cls(username=username, email=email, hashed_password=hashed_password)
        db.add(user)
        db.commit()
        db.refresh(user)
        return user
    
    def verify_password(self, password):
        return pwd_context.verify(password, self.hashed_password)

# Modelo para módulos de inglés
class EnglishModule(Base):
    __tablename__ = "english_modules"
    
    id = Column(Integer, primary_key=True, index=True)
    level = Column(String, index=True)
    title = Column(String, index=True)
    description = Column(String)
    
    @classmethod
    def create(cls, db, level, title, description):
        module = cls(level=level, title=title, description=description)
        db.add(module)
        db.commit()
        db.refresh(module)
        return module
    
    @classmethod
    def get_all(cls, db):
        return db.query(cls).all()
    
    @classmethod
    def get_by_level(cls, db, level):
        return db.query(cls).filter(cls.level == level).all()

# Modelo para el progreso del usuario
class UserProgress(Base):
    __tablename__ = "user_progress"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, index=True)
    module_id = Column(Integer, index=True)
    completed = Column(Boolean, default=True)
    completed_at = Column(DateTime, default=datetime.datetime.utcnow)
    
    @classmethod
    def mark_completed(cls, db, user_id, module_id):
        # Verificar si ya existe un registro
        existing = db.query(cls).filter(cls.user_id == user_id, cls.module_id == module_id).first()
        if existing:
            existing.completed = True
            existing.completed_at = datetime.datetime.utcnow()
            db.commit()
            return existing
        
        # Crear nuevo registro
        progress = cls(user_id=user_id, module_id=module_id, completed=True)
        db.add(progress)
        db.commit()
        db.refresh(progress)
        return progress
    
    @classmethod
    def get_user_completed_modules(cls, db, user_id):
        return db.query(cls.module_id).filter(cls.user_id == user_id, cls.completed == True).all()

# Crear tablas
def create_tables():
    Base.metadata.create_all(bind=engine)

# Obtener sesión de la base de datos
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close() 