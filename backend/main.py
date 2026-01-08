from database import engine, Sale
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from datetime import date
from typing import Optional
from sqlalchemy.orm import Session
from database import SessionLocal
from sqlalchemy import text

class SaleCreate(BaseModel):
    product_id: int
    quantity: int
    sale_date: date
    customer_name: str
    remarks: Optional[str] = None

class SaleResponse(BaseModel):
    sale_id: int
    product_id: int
    quantity: int
    amount: float
    sale_date: date
    customer_name: str
    remarks: Optional[str] = None
    created_at: date

app = FastAPI(title="Sales Management API")

@app.get("/")
def root():
    return {"message": "Backend is running"}

@app.get("/test-db")
def test_db():
    with engine.connect() as conn:
        result = conn.execute(text("SELECT 1"))
        return {"database": "connected", "test_query_result": result.scalar()}

@app.get("/sales", response_model=list[SaleResponse])
def get_all_sales():
    db = SessionLocal()
    try:
        sales = db.query(Sale).order_by(Sale.created_at.desc()).all()
        return sales
    finally:
        db.close()

@app.post("/sales", response_model=SaleResponse)
def create_sale(sale: SaleCreate):
    db = SessionLocal()
    try:
        # Calculate amount (fetch product price * quantity)
        result = db.execute(
            text("SELECT unit_price FROM products WHERE product_id = :product_id"),
            {"product_id": sale.product_id}
        ).fetchone()

        if not result:
            raise HTTPException(status_code=404, detail="Product not found")

        unit_price = result[0]
        amount = unit_price * sale.quantity

        # Create new sale
        new_sale = Sale(
            product_id=sale.product_id,
            quantity=sale.quantity,
            amount=amount,
            sale_date=sale.sale_date,
            customer_name=sale.customer_name,
            remarks=sale.remarks
        )
        db.add(new_sale)
        db.commit()
        db.refresh(new_sale)
        return new_sale
    finally:
        db.close()

@app.put("/sales/{sale_id}", response_model=SaleResponse)
def update_sale(sale_id: int, sale_update: SaleCreate):
    db = SessionLocal()
    try:
        # Find existing sale
        existing = db.query(Sale).filter(Sale.sale_id == sale_id).first()
        if not existing:
            raise HTTPException(status_code=404, detail="Sale not found")

        # Recalculate amount if product_id or quantity changed
        if sale_update.product_id != existing.product_id or sale_update.quantity != existing.quantity:
            result = db.execute(
                text("SELECT unit_price FROM products WHERE product_id = :product_id"),
                {"product_id": sale_update.product_id}
            ).fetchone()
            if not result:
                raise HTTPException(status_code=404, detail="Product not found")
            unit_price = result[0]
            amount = unit_price * sale_update.quantity
        else:
            amount = existing.amount

        # Update fields
        existing.product_id = sale_update.product_id
        existing.quantity = sale_update.quantity
        existing.amount = amount
        existing.sale_date = sale_update.sale_date
        existing.customer_name = sale_update.customer_name
        existing.remarks = sale_update.remarks

        db.commit()
        db.refresh(existing)
        return existing
    finally:
        db.close()
        
@app.delete("/sales/{sale_id}")
def delete_sale(sale_id: int):
    db = SessionLocal()
    try:
        sale = db.query(Sale).filter(Sale.sale_id == sale_id).first()
        if not sale:
            raise HTTPException(status_code=404, detail="Sale not found")
        
        db.delete(sale)
        db.commit()
        return {"message": f"Sale {sale_id} deleted successfully"}
    finally:
        db.close()