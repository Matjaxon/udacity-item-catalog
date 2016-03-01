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
@app.route('/companies/')
def showCompanies():
	companies = session.query(Company).order_by(Company.name)
	return render_template('companies.html', companies = companies)

# Registers a new partner vendor.
@app.route('/companies/add/', methods =['GET', 'POST'])
def addCompany():
	if 'username' not in login_session:
		return redirect('/login')
	if request.method == 'POST':
		newCompany = Company(name = request.form['name'], 
			location = request.form['location'], user_id = login_session['user_id'])
		session.add(newCompany)
		session.commit()
		flash(newCompany.name + " successfully created!  Check your company page to add available items.")
		return redirect(url_for('showCompanies'))
	else:
		return render_template('addCompany.html')

# Edit an existing vendor partner.
@app.route('/companies/<int:company_id>/edit/', methods = ['GET', 'POST'])
def editCompany(company_id):
	if 'username' not in login_session:
		return redirect('/login')
	company = session.query(Company).filter_by(id = company_id).one()
	if company.user_id != login_session['user_id']:
	    return "<script>function myFunction() {alert('You are not authorized to edit this vendor page. \
	    	Please login in to the correct account to make any changes.');}</script> \
<body onload='myFunction()''>"	
	if request.method == 'POST':
		company.name = request.form['name']
		company.location = request.form['location']
		session.commit()
		flash(company.name + " successfully updated.")
		return redirect(url_for('showItems', company_id = company_id))
	else:
		return render_template('editCompany.html', company = company)

# Delete company profile.
@app.route('/companies/<int:company_id>/delete/', methods = ['GET', 'POST'])
def deleteCompany(company_id):
	if 'username' not in login_session:
		return redirect('/login')
	company = session.query(Company).filter_by(id = company_id).one()
	if company.user_id != login_session['user_id']:
	    return "<script>function myFunction() {alert('You are not authorized to make any changes to this vendor page. \
	    	Please login in to the correct account in order to make any changes.');}</script> \
<body onload='myFunction()''>"			
	if request.method == 'POST':
		itemsToDelete = session.query(CatalogItem).filter_by(company_id = company_id).all()
		for item in itemsToDelete:
			session.delete(item)
		session.delete(company)
		session.commit()
		flash(company.name + " successfully deleted.")
		return redirect(url_for('showCompanies'))
	else:
		return render_template('deleteCompany.html', company = company)

# Shows all items across all categories from a given vendor.
@app.route('/companies/<int:company_id>/items/')
def showItems(company_id):
	company = session.query(Company).filter_by(id = company_id).one()
	items = session.query(CatalogItem).filter_by(company_id = company_id).all()
	departments = session.query(CatalogItem.category).filter_by(company_id = company_id).group_by(CatalogItem.category).order_by(CatalogItem.category).all()
	return render_template('vendorCatalogItems.html', company = company, items = items, departments = departments)

# Add a new item to a vendor's catalog.
@app.route('/companies/<int:company_id>/items/new/', methods = ['GET', 'POST'])
def addItems(company_id):
	if 'username' not in login_session:
		return redirect('/login')
	company = session.query(Company).filter_by(id = company_id).one()
	if company.user_id != login_session['user_id']:
	    return "<script>function myFunction() {alert('You are not authorized to make any changes to this vendor page. \
	    	Please login in to the correct account in order to make any changes.');}</script> \
<body onload='myFunction()''>"			
	if request.method == 'POST':
		newItem = CatalogItem(name = request.form['name'], 
			description = request.form['description'], 
			category = request.form['category'], price = request.form['price'],
			company_id = company_id)
		session.add(newItem)
		session.commit()
		flash(newItem.name + " successully added to " + company.name + "'s available items.")
		return redirect(url_for('showItems', company_id = company_id))
	else:
		return render_template('newCatalogItem.html', company = company)

# Edit an existing item.
@app.route('/companies/<int:company_id>/items/<int:item_id>/edit/', methods = ['GET', 'POST'])
def editItem(company_id, item_id):
	if 'username' not in login_session:
		return redirect('/login')
	company = session.query(Company).filter_by(id = company_id).one()
	if company.user_id != login_session['user_id']:
	    return "<script>function myFunction() {alert('You are not authorized to make any changes to this vendor page. \
	    	Please login in to the correct account in order to make any changes.');}</script> \
<body onload='myFunction()''>"		
	item = session.query(CatalogItem).filter_by(id = item_id).one()
	if request.method == 'POST':
		item.name = request.form['name']
		item.description = request.form['description']
		item.price = request.form['price']
		item.category = request.form['category']
		session.commit()
		flash(item.name + " successfully edited.")
		return redirect(url_for('showItems', company_id = company_id))
	else:
		return render_template('editCatalogItem.html', company = company, item = item)

# Delete an existing item.
@app.route('/companies/<int:company_id>/items/<int:item_id>/delete/', methods = ['GET', 'POST'])
def deleteItem(company_id, item_id):
	if 'username' not in login_session:
		return redirect('/login')
	company = session.query(Company).filter_by(id = company_id).one()
	if company.user_id != login_session['user_id']:
	    return "<script>function myFunction() {alert('You are not authorized to make any changes to this vendor page. \
	    	Please login in to the correct account in order to make any changes.');}</script> \
<body onload='myFunction()''>"		
	item = session.query(CatalogItem).filter_by(id = item_id).one()
	if request.method == 'POST':
		session.delete(item)
		session.commit()
		flash(item.name + " successfully deleted.")
		return redirect(url_for('showItems', company_id = company_id))
	else:
		return render_template('deleteCatalogItem.html', company = company, item = item)

@app.route('/login/')
def showLogin():
  state = ''.join(random.choice(string.ascii_uppercase + string.digits) for x 
    in xrange(32))
  print state
  login_session['state'] = state
  return render_template('login.html', STATE = state)


#-----------------------------------------------------------------------

# API ENDPOINTS

#-----------------------------------------------------------------------


#JSON APIs to view Restaurant Information
@app.route('/companies/<int:company_id>/items/JSON')
def showItemsJSON(company_id):
    company = session.query(Company).filter_by(id = company_id).one()
    items = session.query(CatalogItem).filter_by(company_id = company_id).all()
    return jsonify(Items=[i.serialize for i in items])


@app.route('/companies/<int:company_id>/items/<int:item_id>/JSON')
def vendorItemJSON(company_id, item_id):
    item = session.query(CatalogItem).filter_by(id = item_id).one()
    return jsonify(Vendor_Item = Vendor_Item.serialize)

@app.route('/coimpanies/JSON')
def compnaiesJSON():
    companies = session.query(Company).all()
    return jsonify(Companies = [r.serialize for c in companies])


#-----------------------------------------------------------------------

# LOGIN USING GOOGLE OR FACEBOOK

#-----------------------------------------------------------------------


CLIENT_ID = json.loads(
  open('gconnect_client_secrets.json', 'r').read())['web']['client_id']
APPLICATION_NAME = "Udacity Item Catalog App Credentials"

def getUserInfo(user_id):
  user = session.query(Users).filter_by(id = user_id).one()
  return user

def getUserID(email):
  try:
    user = session.query(Users).filter_by(email = email).one()
    return user.id
  except:
    return None

def createUser(login_session):
  newUser = Users(name = login_session['username'], email = login_session['email'],
    picture = login_session['picture'])
  session.add(newUser)
  session.commit()
  user = session.query(Users).filter_by(email = login_session['email']).one()
  return user.id

def getOwnerID(company_id):
  company = session.query(Company).filter_by(id = company_id).one()
  ownerID = company.user_id
  # print ownerID
  return ownerID


# Login using Google Sign In.
@app.route('/gconnect', methods = ['POST'])
def gconnect():
  print ("gconnect started.")
  if request.args.get('state') != login_session['state']:
    response = make_response(json.dumps('Invalid state parameter'), 401)
    response.headers['Content-Type'] = 'application/json'
    return response
  code = request.data

  try: 
    # Upgrade the authorization code into a credential object
    oauth_flow = flow_from_clientsecrets('gconnect_client_secrets.json', scope = '')
    oauth_flow.redirect_uri = 'postmessage'
    credentials = oauth_flow.step2_exchange(code)
  except FlowExchangeError:
    response = make_response(json.dumps("Failed to upgrade the authorization code."), 401)
    response.headers['Content-Type'] = 'application/json'
    return response

  #Check that authentication token is valid.
  access_token = credentials.access_token
  url = ('https://www.googleapis.com/oauth2/v1/tokeninfo?access_token={}'.format(access_token))
  h = httplib2.Http()
  result = json.loads(h.request(url, 'GET')[1])
  # If there was an error in the access token info, abort.
  if result.get('error') is not None:
    response = make_response(json.dumps(result.get('error')), 500)
    reponse.headers['Content-Type'] = 'application/json'

  # Verify that the access token is used for the intended user.
  gplus_id = credentials.id_token['sub']
  if result['user_id'] != gplus_id:
    response = make_response(
      json.dumps("Token's user ID doesn't match given user ID."), 401)
    response.headers['Content-Type'] = 'application/json'
    return response

  # Verify that the access token is valid for this app.
  if result['issued_to'] != CLIENT_ID:
    response = make_response(
      json.dumps("Token's client ID does not match app's."), 401)
    print "Token's client ID does not match app's."
    response.headers['Content-Type'] = 'application/json'
    return response

  # Check to see if user is already logged in.
  stored_credentials = login_session.get('credentials')
  stored_gplus_id = login_session.get('gplus_id')
  if stored_credentials is not None and gplus_id == stored_gplus_id:
    response = make_response(json.dumps('Current user already connected.'), 200)
    response.headers['Content-Type'] = 'application/json'

  # Store the access token in the session for later
  login_session['provider'] = 'google'
  login_session['credentials'] = credentials
  login_session['gplus_id'] = gplus_id

  # Get user info
  userinfo_url = "https://www.googleapis.com/oauth2/v1/userinfo"
  params = {'access_token': credentials.access_token, 'alt': 'json'}
  print params
  answer = requests.get(userinfo_url, params = params)
  data = answer.json()

  login_session['username'] = data['name']
  login_session['picture'] = data['picture']
  login_session['email'] = data['email']

  # See if user exists, if it doesn't make a new one.
  user_id = getUserID(login_session['email'])
  if not user_id:
    user_id = createUser(login_session)
  login_session['user_id'] = user_id

  output = ''
  output += '<h1>Welcome, '
  output += login_session['username']
  output += '!</h1>'
  output += '<img src=" '
  output += login_session['picture']
  output += ' " style = "width: 300px; height: 300px; border-radius: 150px; '
  output += ' -webkit-border-radius: 150px; -moz-border-radius: 150px;">'
  flash('You are now logged in as {}'.format(login_session['username']))
  return output
  print "End of login code."

# Login using Facebook Log in
@app.route('/fbconnect', methods = ['POST'])
def fbconnect():
  print ("fbconnect started.")
  if request.args.get('state') != login_session['state']:
    response = make_response(
      json.dumps('Invalid state parameter.'), 401)
    response.headers['Content-Type'] = 'application/json'
    return response

  access_token = request.data
  print ("access token received {0}".format(access_token))

  # Exchange client token for long-lived server-side token with GET /oauth/
  # access_token?grant_type=fb_exchange_token&client_id={app-id}&client_sercret \
  # ={app-secret}&fb_exchange_token={short-lived-token}
  app_id = json.loads(
  	open('fb_client_secrets.json', 'r').read())['web']['app_id']
  print ("App ID: {0}".format(app_id))
  app_secret = json.loads(
    open('fb_client_secrets.json', 'r').read())['web']['app_secret']
  print ("App Secret: {0}".format(app_secret))
  url = 'https://graph.facebook.com/oauth/access_token?grant_type=fb_exchange_token&client_id={0}&client_secret={1}&fb_exchange_token={2}'.format(app_id, 
    app_secret, access_token)
  h = httplib2.Http()
  result = h.request(url, 'GET')[1]

  # Use token to get user info from API
  userinfo_url = 'https://graph.facebook.com/v2.5/me'
  # strip expire tag from access token
  token = result.split("&")[0]

  url = 'https://graph.facebook.com/v2.5/me?{0}&fields=name,id,email'.format(token)

  h = httplib2.Http()
  result = h.request(url, 'GET')[1]
  print ("url sent from API access:{0}".format(url))
  print "API JSON result: {0}".format(result)
  data = json.loads(result)
  login_session['provider'] = 'facebook'
  login_session['username'] = data['name']
  login_session['email'] = data['email']
  login_session['facebook_id'] = data['id']

  # The tokoen must be stored in the login_session in order to properly logout, let's strip out the information before the equals sign in our token.
  stored_token = token.split("=")[1]
  login_session['access_token'] = stored_token

  # Get user picture
  url = 'https://graph.facebook.com/v2.5/me/picture?{0}&redirect=0&height=200&width=200'.format(token)
  h = httplib2.Http()
  result = h.request(url, 'GET')[1]
  data = json.loads(result)

  login_session['picture'] = data['data']['url']

  # See if user exists
  user_id = getUserID(login_session['email'])
  if not user_id:
    user_id = createrUser(login_session)
  login_session['user_id'] = user_id

  output = ''
  output += '<h1>Welcome, '
  output += login_session['username']

  output += '!</h1>'
  output += '<img src='
  output += login_session['picture']
  output += ' "style = "width: 300px; height: 300px; border-radius: 150px; -webkit-border-radius: 150px; -moz-border-radius: 150px; -moz-border-radius: 150px;">'

  flash("Now logged in as {0}".format(login_session['username']))
  return output

# DISCONNECT - Revoke a current user's token and reset their login_session.
@app.route('/gdisconnect')
def gdisconnect():
  # Only disconnect a connecter user.
  print login_session
  credentials = login_session.get('credentials')
  if credentials is None:  # if credentials is empty then nobody is logged in.
    response = make_response(
      json.dumps('Current user not connected.'), 401)
    response.headers['Content-Type'] = 'application/json'
    return response
  # Execute HTTP GET request to revoke current token.
  access_token = credentials.access_token
  url = 'https://accounts.google.com/o/oauth2/revoke?token={0}'.format(access_token)
  h = httplib2.Http()
  result = h.request(url, "GET")[0]

  if result['status'] != '200':
    # For whatever reason, the given token was invalid.
    response = make_response(
      json.dumps('Failed to revoke token for given user.'), 400)
    response.headers['Content-Type'] = 'application/json'
    return response

@app.route('/fbdisconnect')
def fbdisconnect():
  facebook_id = login_session['facebook_id']
  # The access token must be  included to successfully logout
  access_token = login_session['access_token']
  url = 'https://graph.facebook.com/{0}/permissions'.format(facebook_id)
  h = httplib2.Http()
  result = h.request(url, 'DELETE')[1]
  return "you have been logged out"

# Allows for a single url to be hit to disconnect for both Google and Facebook.
@app.route('/disconnect')
def disconnect():
  if 'provider' in login_session:
    if login_session['provider'] == 'google':
      gdisconnect()
      del login_session['gplus_id']
      del login_session['credentials']
    if login_session['provider'] == 'facebook':
      fbdisconnect()
      del login_session['facebook_id']
    del login_session['username']
    del login_session['email']
    del login_session['picture']
    del login_session['user_id']
    del login_session['provider']
    flash ("You have been successfully logged out.")
    return redirect(url_for('showCategories'))

  else:
    flash ("You were not logged in to begin with!")
    return redirect(url_for('showCategories'))

#---------------------------------------------------------------------

if __name__ == '__main__':
  app.secret_key = 'super_secret_key'
  app.debug = True
  app.run(host = '0.0.0.0', port = 5000)