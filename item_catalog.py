from flask import Flask, render_template, request, redirect, jsonify
from flask import url_for, flash, make_response
from flask import session as login_session
app = Flask(__name__)

from sqlalchemy import create_engine, asc
from sqlalchemy.orm import sessionmaker
from database_setup import Base, Company, Users, CatalogItem

import random, string, requests, httplib2, json

from oauth2client.client import flow_from_clientsecrets

from oauth2client.client import FlowExchangeError


#Connect to Database and create database session
engine = create_engine('postgresql:///item_catalog')
Base.metadata.bind = engine

DBSession = sessionmaker(bind=engine)
session = DBSession()

#----------------------------------------------------------------------




#----------------------------------------------------------------------

# Home page showing list of all categories.
@app.route('/')
@app.route('/categories/')
def showCategories():
	departments = session.query(CatalogItem.category).group_by(CatalogItem.category).order_by(CatalogItem.category).all()
	return render_template('categories.html', departments = departments)

# Page showing all items within a category.
@app.route('/categories/<department>/')
def showCategoryItems(department):
	items = session.query(CatalogItem).filter_by(category = department)
	return render_template('departmentItems.html', items = items, department = department)

# Shows all partner vendor companies.
@app.route('/companies')
def showCompanies():
	companies = session.query(Company).order_by(Company.name)
	return render_template('companies.html', companies = companies)

# Registers a new partner vendor.
@app.route('/companies/add', methods =['GET', 'POST'])
def addCompany():
	if request.method == 'POST':
		newCompany = Company(name = request.form['name'], 
			location = request.form['location'], user_id = 1) #Set user_id to 1 for now to associate with Admin.
		session.add(newCompany)
		session.commit()
		return redirect(url_for('showCompanies'))
	else:
		return render_template('addCompany.html')

# Shows all items across all categories from a given vendor.
@app.route('/companies/<int:company_id>/items')
def showItems(company_id):
	company = session.query(Company).filter_by(id = company_id).one()
	items = session.query(CatalogItem).filter_by(company_id = company_id).all()
	departments = session.query(CatalogItem.category).filter_by(company_id = company_id).group_by(CatalogItem.category).order_by(CatalogItem.category).all()
	return render_template('vendorCatalogItems.html', company = company, items = items, departments = departments)

# Add a new item to a vendor's catalog.
@app.route('/companies/<int:company_id>/items/new', methods = ['GET', 'POST'])
def addItems(company_id):
	company = session.query(Company).filter_by(id = company_id).one()
	if request.method == 'POST':
		newItem = CatalogItem(name = request.form['name'], 
			description = request.form['description'], 
			category = request.form['category'], price = request.form['price'],
			company_id = company_id)
		session.add(newItem)
		session.commit()
		return redirect(url_for('showItems', company_id = company_id))
	else:
		return render_template('newCatalogItem.html', company = company)



#---------------------------------------------------------------------

if __name__ == '__main__':
  # app.secret_key = 'super_secret_key'
  app.debug = True
  app.run(host = '0.0.0.0', port = 5000)