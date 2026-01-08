from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from datetime import date

DATABASE_URL = "mysql+pymysql://root:Jagan7nathan&@localhost:3306/sales_db"

engine = create_engine(DATABASE_URL)

SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine
)

Base = declarative_base()

from sqlalchemy import Column, Integer, String, DECIMAL, Date, ForeignKey
from sqlalchemy.orm import relationship

class Sale(Base):
    __tablename__ = "sales"

    sale_id = Column(Integer, primary_key=True, index=True)
    product_id = Column(Integer, nullable=False)
    quantity = Column(Integer, nullable=False)
    amount = Column(DECIMAL(10, 2), nullable=False)
    sale_date = Column(Date, nullable=False)
    customer_name = Column(String(100), nullable=False)
    remarks = Column(String(255), nullable=True)
    created_at = Column(Date, default=date.today, nullable=False)
