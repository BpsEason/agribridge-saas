from sqlalchemy import Column, Integer, String, Float, ForeignKey
from sqlalchemy.orm import declarative_base, relationship

Base = declarative_base()

class Tenant(Base):
    __tablename__ = "tenants"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), unique=True)
    farmers = relationship("Farmer", back_populates="tenant") # One-to-many with Farmer
    products = relationship("Product", back_populates="tenant") # One-to-many with Product
    orders = relationship("Order", back_populates="tenant") # One-to-many with Order

class Farmer(Base):
    __tablename__ = "farmers"
    id = Column(Integer, primary_key=True, index=True)
    tenant_id = Column(Integer, ForeignKey("tenants.id"), index=True)  # Multi-tenant support
    name = Column(String(255), index=True)
    location = Column(String(255))
    esg_score = Column(Float, default=0.0)
    total_sales = Column(Float, default=0.0)
    tenant = relationship("Tenant", back_populates="farmers") # Many-to-one with Tenant
    products = relationship("Product", back_populates="farmer") # One-to-many with Product

class Product(Base):
    __tablename__ = "products"
    id = Column(Integer, primary_key=True, index=True)
    tenant_id = Column(Integer, ForeignKey("tenants.id"), index=True)  # Multi-tenant support
    name = Column(String(255))
    price = Column(Float)
    farmer_id = Column(Integer, ForeignKey("farmers.id"))
    tenant = relationship("Tenant", back_populates="products") # Many-to-one with Tenant
    farmer = relationship("Farmer", back_populates="products") # Many-to-one with Farmer

class Order(Base):
    __tablename__ = "orders"
    id = Column(Integer, primary_key=True, index=True)
    tenant_id = Column(Integer, ForeignKey("tenants.id"), index=True)  # Multi-tenant support
    product_id = Column(Integer, ForeignKey("products.id"))
    quantity = Column(Integer)
    total_price = Column(Float)
    buyer_id = Column(Integer) # Mock buyer ID
    status = Column(String(50))
    tenant = relationship("Tenant", back_populates="orders") # Many-to-one with Tenant
    product = relationship("Product") # Many-to-one with Product
