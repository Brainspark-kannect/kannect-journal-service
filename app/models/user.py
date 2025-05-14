# app/models/user.py
from sqlalchemy import Column, Integer, String, Boolean, DateTime, Table, ForeignKey
from sqlalchemy.orm import relationship
from app.db.base import Base

# Many-to-many relationship table for users and roles
user_roles = Table(
    'user_roles',
    Base.metadata,
    Column('user_id', Integer, ForeignKey('users.id')),
    Column('role_id', Integer, ForeignKey('roles.id'))
)

class Role(Base):
    __tablename__ = "roles"
    
    id = Column(Integer, primary_key=True)
    role_name = Column(String(50), unique=True, nullable=False)
    
    # Back reference to users
    users = relationship("User", secondary=user_roles, back_populates="roles")
    
    def __repr__(self):
        return f"<Role {self.role_name}>"

class User(Base):
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True)
    email = Column(String(100), unique=True, nullable=False)
    user_name = Column(String(100), unique=True, nullable=False)
    password = Column(String(255), nullable=False)
    first_name = Column(String(100))
    last_name = Column(String(100))
    department = Column(String(100))
    tech_stack = Column(String(100))
    profile_photo_url = Column(String(255))
    active = Column(Boolean, default=False)
    wallet_balance = Column(Integer, default=0)
    last_login = Column(DateTime)
    
    # Relationship with roles
    roles = relationship("Role", secondary=user_roles, back_populates="users", lazy="joined")
