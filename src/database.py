import os
from datetime import datetime
import contextlib

from sqlalchemy import create_engine, Column, Integer, String, DateTime
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker


DATABASE_URL = os.environ.get("DATABASE_URL")
Base = declarative_base()

class Product(Base):
    __tablename__ = 'parsed_products'

    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)
    type = Column(String)
    price = Column(String)
    rating = Column(String)
    reviews = Column(String)
    link = Column(String, unique=True)
    parse_date = Column(DateTime)

class Database:
    def __init__(self):
        self.engine = create_engine(DATABASE_URL)
        self.SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=self.engine)
        Base.metadata.create_all(bind=self.engine)

    @contextlib.contextmanager
    def get_session(self):
        session = self.SessionLocal()
        try:
            yield session
        finally:
            session.close()

    def save_products(self, products):
        with self.get_session() as session:
            for product in products:
                existing_product = session.query(Product).filter_by(link=product['link']).first()
                if existing_product:
                    existing_product.name = product['name']
                    existing_product.type = product['type']
                    existing_product.price = product['price']
                    existing_product.rating = product['rating']
                    existing_product.reviews = product['reviews']
                    existing_product.parse_date = datetime.utcnow()
                else:
                    db_product = Product(
                        name=product['name'],
                        type=product['type'],
                        price=product['price'],
                        rating=product['rating'],
                        reviews=product['reviews'],
                        link=product['link'],
                        parse_date=datetime.utcnow()
                    )
                    session.add(db_product)

            session.commit()
            print(f"Saved/updated {len(products)} products")

    def get_products(self, limit=10):
        with self.get_session() as session:
            products = session.query(Product).order_by(Product.parse_date.desc()).limit(limit).all()
            return [
                {
                    "name": product.name,
                    "type": product.type,
                    "price": product.price,
                    "rating": product.rating,
                    "reviews": product.reviews,
                    "link": product.link,
                    "parse_date": product.parse_date.isoformat()
                }
                for product in products
            ]