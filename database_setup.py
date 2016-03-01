from sqlalchemy import Column, ForeignKey, Integer, String
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from sqlalchemy import create_engine
import os
import sys
 
Base = declarative_base()

class Users(Base):
  __tablename__ = 'users'
  id = Column(Integer, primary_key=True)
  name = Column(String(250), nullable =False)
  email = Column(String(250), nullable = False)
  picture = Column(String(250))

  @property
  def serialize(self):
    """Return object data in easily serializable format"""
    return {
          'id' : self.id,
          'name' : self.name,
          'email' : self.email,
          'picture' : self.picture,
    }


class Company(Base):
  __tablename__ = 'company'
 
  id = Column(Integer, primary_key=True)
  name = Column(String(250), nullable=False)
  location = Column(String(250), nullable=False)
  user_id = Column(Integer, ForeignKey('users.id'))
  user = relationship(Users)

  @property
  def serialize(self):
     """Return object data in easily serializeable format"""
     return {
         'name'         : self.name,
         'id'           : self.id,
         'location'     : self.location,
         'user_id'      : self.user_id,
       }
 

class CatalogItem(Base):
  __tablename__ = 'catalog_item'

  name =Column(String(100), nullable = False)
  id = Column(Integer, primary_key = True)
  description = Column(String(250))
  price = Column(String(8))
  category = Column(String(250))
  company_id = Column(Integer,ForeignKey('company.id'))
  company = relationship(Company)
  picture = Column(String(250))

  @property
  def serialize(self):
     """Return object data in easily serializeable format"""
     return {
         'name'         : self.name,
         'description'  : self.description,
         'id'           : self.id,
         'price'        : self.price,
         'category'     : self.category,
         'company_id'   : self.company_id,
         'company'      : self.company.name,
       }


engine = create_engine('postgresql:///item_catalog')
 

Base.metadata.create_all(engine)
