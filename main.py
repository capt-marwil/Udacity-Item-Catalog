from flask import Flask, render_template, request, redirect, jsonify, url_for, \
    flash, make_response
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, relationship
from flask_wtf import Form
from wtforms import StringField, SubmitField, TextField, FileField
from wtforms.validators import DataRequired
from setup_database import Base, expeditions_categories, Expedition, Item, Category, User
from flask import session as login_session
from oauth2client.client import flow_from_clientsecrets
from oauth2client.client import FlowExchangeError
import httplib2
import json
import requests
import random
import string
from xml.etree.ElementTree import dump, Element, SubElement


app = Flask(__name__)

CLIENT_ID = json.loads(
    open('client_secrets.json', 'r').read())['web']['client_id']
APPLICATION_NAME = "Expedition Packing list App"



""" Connect to Database and create a database session """
engine = create_engine('sqlite:///catalog.db')
Base.metadata.bind = engine

DBSession = sessionmaker(bind=engine)
session = DBSession()


""" Routes """

""" routes that don't require an login """


@app.route('/')
@app.route('/catalog')
def index():
    expeditions = session.query(Expedition).order_by(Expedition.title)
    if 'username' not in login_session:
        return render_template('public_index.html',
                               expeditions=expeditions)
    else:
        return render_template('index.html',
                               expeditions=expeditions)


@app.route('/expedition/<int:expedition_id>')
def expedition(expedition_id):
    expedition = session.query(Expedition).filter_by(id=expedition_id).one()
    categories = session.query(Category).filter(Category.expedition.any(
        id=expedition_id))
    print str()
    if 'username' not in login_session:
        return render_template('public_expedition.html',
                               expedition=expedition,
                               categories=categories)
    else:
        return render_template('expedition.html',
                               expedition=expedition,
                               categories=categories)


@app.route('/expedition/<int:expedition_id>/category/<int:category_id>')
def category(expedition_id, category_id):
    expedition = session.query(Expedition).filter_by(id=expedition_id).one()
    category = session.query(Category).filter_by(id=category_id).one()
    items = session.query(Item).filter_by(category_id=category_id,
                                          expedition_id=expedition_id)
    return render_template('category.html', category=category,
                                            expedition=expedition,
                                            items=items)


@app.route('/expedition/<int:expedition_id>/category/<int:category_id>/'
           'item/<int:item_id>', methods=['GET', 'POST'])
def item(expedition_id, category_id, item_id):
    pass


""" routes to login and to logout """


# Create anti-forgery state token
@app.route('/login')
def showLogin():
    state = ''.join(random.choice(string.ascii_uppercase + string.digits)
                    for x in xrange(32))
    login_session['state'] = state
    # return "The current session state is %s" % login_session['state']
    return render_template('login.html', STATE=state)


@app.route('/gconnect', methods=['POST'])
def gconnect():
    # Validate state token
    if request.args.get('state') != login_session['state']:
        response = make_response(json.dumps('Invalid state parameter.'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response
    # Obtain authorization code
    code = request.data

    try:
        # Upgrade the authorization code into a credentials object
        oauth_flow = flow_from_clientsecrets('client_secrets.json', scope='')
        oauth_flow.redirect_uri = 'postmessage'
        credentials = oauth_flow.step2_exchange(code)
    except FlowExchangeError:
        response = make_response(
            json.dumps('Failed to upgrade the authorization code.'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Check that the access token is valid.
    access_token = credentials.access_token
    url = ('https://www.googleapis.com/oauth2/v1/tokeninfo?access_token=%s'
           % access_token)
    h = httplib2.Http()
    result = json.loads(h.request(url, 'GET')[1])
    # If there was an error in the access token info, abort.
    if result.get('error') is not None:
        response = make_response(json.dumps(result.get('error')), 500)
        response.headers['Content-Type'] = 'application/json'

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

    stored_access_token = login_session.get('access_token')
    stored_gplus_id = login_session.get('gplus_id')
    if stored_access_token is not None and gplus_id == stored_gplus_id:
        response = make_response(json.dumps('Current user is already connected.'),
                                 200)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Store the access token in the session for later use.
    login_session['access_token'] = credentials.access_token
    login_session['gplus_id'] = gplus_id

    # Get user info
    userinfo_url = "https://www.googleapis.com/oauth2/v1/userinfo"
    params = {'access_token': credentials.access_token, 'alt': 'json'}
    answer = requests.get(userinfo_url, params=params)

    data = answer.json()

    login_session['username'] = data['name']
    login_session['picture'] = data['picture']
    login_session['email'] = data['email']

    # check whether user exists in local database
    if getUserID(login_session['email']):
        getUserInfo(getUserID(login_session['email']))
    else:
        createUser(login_session)


    output = ''
    output += '<h1>Welcome, '
    output += login_session['username']
    output += '!</h1>'
    output += '<img src="'
    output += login_session['picture']
    output += ' " style = "width: 300px; height: 300px;border-radius: 150px;-webkit-border-radius: 150px;-moz-border-radius: 150px;"> '
    flash("you are now logged in as %s" % login_session['username'])
    print "done!"
    return output

    # DISCONNECT - Revoke a current user's token and reset their login_session


@app.route('/gdisconnect')
def gdisconnect():
    access_token = login_session['access_token']
    print 'In gdisconnect access token is %s', access_token
    print 'User name is: '
    print login_session['username']
    if access_token is None:
        print 'Access Token is None'
        response = make_response(json.dumps('Current user not connected.'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response
    url = 'https://accounts.google.com/o/oauth2/revoke?token=%s' % login_session['access_token']
    h = httplib2.Http()
    result = h.request(url, 'GET')[0]
    print 'result is '
    print result
    if result['status'] == '200':
        del login_session['access_token']
        del login_session['gplus_id']
        del login_session['username']
        del login_session['email']
        del login_session['picture']
        response = make_response(json.dumps('Successfully disconnected.'), 200)
        response.headers['Content-Type'] = 'application/json'
        return response
    else:
        response = make_response(json.dumps('Failed to revoke token for given user.', 400))
        response.headers['Content-Type'] = 'application/json'
        return response


@app.route('/fbconnect', methods=['POST'])
def fbconnect():
    if request.args.get('state') != login_session['state']:
        response = make_response(json.dumps('Invalid state parameter.'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response
    access_token = request.data


    app_id = json.loads(open('fb_client_secret.json', 'r').read())['web']['app_id']
    app_secret = json.loads(open('fb_client_secret.json', 'r').read())['web']['app_secret']

    url = "https://graph.facebook.com/oauth/access_token?grant_type=fb_exchange_token&client_id=%s&client_secret=%s&fb_exchange_token=%s" % (app_id, app_secret, access_token)

    h = httplib2.Http()
    result = h.request(url, 'GET')[1]

    """ Use token to get user info from API """
    userinfo_url = "https://graph.facebook.com/v2.4/me"
    """ strip expire tag from access token """
    token = result.split("&")[0]


    url = 'https://graph.facebook.com/v2.5/me?%s&fields=name,id,email' % token
    h = httplib2.Http()
    result = h.request(url, 'GET')[1]
    # DEBUG output
    print "url sent for API access: %s" % url
    print "API JSON result: %s" % result
    data = json.loads(result)
    login_session['provider'] = 'facebook'
    login_session['username'] = data["name"]
    login_session['email'] = data["email"]
    login_session['facebook_id'] = data["id"]

    # The token must be stored in the login_session in order to properly logout, let's strip out the information before the equals sign in our token
    stored_token = token.split("=")[1]
    login_session['access_token'] = stored_token

    # get user picture

    url = "https://graph.facebook.com/v2.5/me/picture?%s&redirect=0&height=200&width=200" % token
    h = httplib2.Http()
    result = h.request(url, 'GET')[1]
    data = json.loads(result)

    login_session['picture'] = data["data"]["url"]

    # see if user exists in local database
    user_id = getUserID(login_session['email'])
    if not user_id:
        user_id = createUser(login_session)
    login_session['user_id'] = user_id

    output = ''
    output += '<h1>Welcome, '
    output += login_session['username']
    output += '!</h1>'
    output += '<img src="'
    output += login_session['picture']
    output += ' " style = "width: 300px; height: 300px;border-radius: 150px;-webkit-border-radius: 150px;-moz-border-radius: 150px;"> '
    flash("you are now logged in as %s" % login_session['username'])
    print "done!"
    return output



@app.route('/fbdisconnet')
def fbdisconnect():
    facebook_id = login_session['facebook_id']
    access_token = login_session['access_token']
    url = 'https://graph.facebook.com/%s/permissions?access_token=%s' % (facebook_id, access_token)
    h = httplib2.Http()
    result = h.request(url, 'DELETE')[1]
    del login_session['username']
    del login_session['email']
    del login_session['picture']
    del login_session['facebook_id']
    return "You have been logged out"


@app.route('/login')
def login():
    return render_template('login.html')


@app.route('/disconnet')
def disconnet():
    pass

""" routes to add, edit and delete database entities require a valid login """

""" routes to manipulate Expdition entity """
@app.route('/expedition/new', methods=['GET', 'POST'])
def addExpedition():
    if 'username' not in login_session:
        return redirect('/login')
    if request.method == 'POST':
        user_id = getUserID(login_session['email'])
        newExpedition = Expedition(title=request.form['title'],
                                   description=request.form['description'],
                                   picture=request.form['picture'],
                                   user_id=user_id)
        session.add(newExpedition)
        flash('New Expedition %s has been created' % newExpedition.title)
        session.commit()
        return redirect(url_for('expedition',
                                expedition_id=newExpedition.id))
    else:
        return render_template('addExpedition.html')


@app.route('/expedition/<int:expedition_id>/edit', methods=['GET', 'POST'])
def editExpedition(expedition_id):
    """
    Checks whether user is logged in
    If called with GET displays form to edit an expedition record
    If called with POST checks whether user is logged in and allowed to edit
     the record.
    If so stores edited data and redirects user to expedition overview
    :param expedition_id:
    :return: editExpedition.html or expedition.html
    """
    editedExpediton = session.query(Expedition).filter_by(id=expedition_id).one()
    user_id = getUserID(login_session['email'])
    if 'username' not in login_session:
        return redirect('/login')
    if editedExpediton.user_id != user_id:
        return "You are not allowed to edit this expedition. Only Users how created an expedition are allowed to edit the informaiton."
    if request.method == 'POST':
        if request.form['title']:
            editedExpediton.title = request.form['title']
        if request.form['description']:
            editedExpediton.description = request.form['description']
        if request.form['picture']:
            editedExpediton.picture = request.form['picture']
        session.add(editedExpediton)
        session.commit()
        flash('You have successsfully edited your expedition.')
        return redirect(url_for('expedition',
                                expedition_id=expedition_id))
    else:
        return render_template('editExpedition.html',
                               expedition=editedExpediton)



@app.route('/expedition/<int:expedition_id>/'
           'delete', methods=['GET', 'POST'])
def deleteExpedition(expedition_id):
    """
    checks whether user is logged in
    If called with GET displays form to delete an expedition record
    If called with POST deletes the record.
    :param expedition_id:
    :return: deleteExpedition.html or expedition.html
    """
    deleteExpedition = session.query(Expedition).filter_by(id=expedition_id).one()
    user_id = getUserID(login_session['email'])
    if 'username' not in login_session:
        return redirect('/login')
    if deleteExpedition.user_id != user_id:
        return "You are not allowed to delete this expedition. Users can only delete Expeditions they created"
    if request.method == 'POST':
        session.delete(deleteExpedition)
        session.commit()
        flash('%s successfully deleted' % deleteExpedition.title)
        return redirect(url_for('index'))
    else:
        return render_template('deleteExpedition.html',
                               expedition=deleteExpedition)


""" routes to manipulate Category entities """


@app.route('/expedition/<int:expedition_id>/category/new/',
           methods=['GET', 'POST'])
def addCategory(expedition_id):
    """
    checks whether user is logged in
    If called with GET displays form to add a category
    If called with POST adds the record.
    :param expedition_id:
    :return: addCategory.html, expedition, login
    """
    expedition = session.query(Expedition).filter_by(id=expedition_id).one()
    user_id = getUserID(login_session['email'])
    if 'username' not in login_session:
        return redirect('/login')
    if request.method == 'POST':
        newCategory = Category(name=request.form['name'],
                               description=request.form['description'],
                               picture=request.form['picture'],
                               user_id=user_id)
        expedition.category.append(newCategory)
        #newCategory.expedition.append(expedition)
        session.add(newCategory)
        session.commit()
        items = session.query(Item).filter_by(id=newCategory.id).all()
        flash('%s added as a new category.' % newCategory.name)
        return redirect(url_for('expedition',
                                expedition_id=expedition.id,
                                category=newCategory,
                                items=items))
    else:
        return render_template('addCategory.html',
                               expedition=expedition)

#/expedition/3/category/4/edit
@app.route('/expedition/<int:expedition_id>/category/<int:category_id>/edit',
           methods=['GET', 'POST'])
def editCategory(expedition_id, category_id):
    """
    checks whether user is logged in
    If called with GET displays form to edit a category
    If called with POST saves the record.
    :param expedition_id:
    :param category_id:
    :return: editCategory.html, category.html, login.html
    """
    editCategory = session.query(Category).filter_by(id=category_id).filter(Category.expedition.any(id=expedition_id)).first()
    user_id = getUserID(login_session['email'])
    if 'username' not in login_session:
        return redirect('/login')
    if editCategory.user_id != user_id:
        return "Your are not allowed to edit this category. Users are only allowed to edit their own categories."
    if request.method == 'POST':
        if request.form['name']:
            editCategory.name = request.form['name']
        if request.form['description']:
            editCategory.description = request.form['description']
        if request.form['picture']:
            editCategory.picture = request.form['picture']
        session.add(editCategory)
        session.commit()
        flash('You have successsfully edited your Category.')
        return redirect(url_for('category',
                                expedition_id=expedition_id,
                                category_id=editCategory.id))
    else:
        return render_template('editCategory.html',
                               expedition_id=expedition_id,
                               category=editCategory)


@app.route('/expedition/<int:expedition_id>/category/<int:category_id>/'
           'delete', methods=['GET', 'POST'])
def deleteCategory(expedition_id, category_id):
    deleteCategory = session.query(Category).filter_by(id=category_id).filter(Category.expedition.any(id=expedition_id)).first()
    user_id = getUserID(login_session['email'])
    if 'username' not in login_session:
        return redirect('/login')
    if deleteCategory.user_id != user_id:
        return "You are not allowed to deleted this category. Users are only allowed to delete categories they created."
    if request.method == 'POST':
        session.delete(deleteCategory)
        session.commit()
        flash("You have succesfully deleted %s " % deleteCategory.name)
        return redirect(url_for('expedition',
                                expedition_id=expedition_id))
    else:
        render_template('deleteCategory.html',
                        expedition_id=expedition_id,
                        category_id=category_id)


""" routes to manipulate Item entity """


@app.route('/expedition/<int:expedition_id>/category/<int:category_id>/item/'
           'new/', methods=['GET', 'POST'])
def addItem(expedition_id, category_id):
    if 'username' not in login_session:
        return redirect('/login')
    if request.method == 'POST':
        user_id = getUserID(login_session['email'])
        newItem = Item(
                    user_id=user_id,
                    category_id=category_id,
                    expediton_id=expedition_id,
                    name=request.form['name'],
                    description=request.form['description'],
                    picture=request.form['picture']
                    )
        session.add(newItem)
        session.commit()
        return redirect(url_for('category'),
                        expedition_id=expedition_id,
                        category_id=category_id)

    else:
        return render_template('addItem.html', expedition_id=expedition_id, category_id=category_id)



@app.route('/expedition/<int:expedition_id>/category/<int:category_id>/item/'
           '<int:item_id>/edit', methods=['GET', 'POST'])
def editItem(expedition_id, category_id, item_id):
    editItem = session.query(Item).filter_by(id=item_id, category_id=category_id, expedition_id=expedition_id)
    user_id = getUserID(login_session['email'])
    if 'username' not in login_session:
        return redirect('/login')
    if editItem.user_id != user_id:
        return "Your are not allowed to edit this item. Users are only allowed to edit Items they created."
    if request.method == 'POST':
        if request.form['name']:
            editItem.name = request.form['name']
        if request.form['descripttion']:
            editItem.description = request.form['description']
        if request.form['picture']:
            editItem.picture = request.form['picture']
        session.add(editItem)
        session.commit()
        flash("%s has been edited and saved." % editItem.name)
        return redirect(url_for('category',
                                expedition_id=expedition_id,
                                category_id=category_id))
    else:
        return render_template('editItem.html',
                               expedition_id=expedition_id,
                               category_id=category_id,
                               item=editItem)


@app.route('/expedition/<int:expedition_id>/category/<int:category_id>/item/'
           '<int:item_id>/delete/', methods=['GET', 'POST'])
def deleteItem(expedition_id, category_id, item_id):
    deleteItem = session.query(Item).filter_by(id=item_id, category_id=category_id, expedition_id=expedition_id)
    user_id = createUser(login_session['email'])
    if 'username' not in login_session:
        return redirect('/login')
    if deleteItem.user_id != user_id:
        return "You are not allowed to delete this item. Users are only allowed to delete items they created."
    if request.method == 'POST':
        session.delete(deleteItem)
        session.commit()
        flash('You have successfully deleted %s' % deleteItem.name)
    else:
        return render_template('deleteItem.html',
                               expedition_id= expedition_id,
                               category_id=category_id,
                               item=deleteItem)


""" Create and edit Users in the database """
def getUserID(email):
    try:
        user = session.query(User).filter_by(email=email).one()
        return user.id
    except:
        return None


def getUserInfo(user_id):
    user = session.query(User).filter_by(id=user_id).one()
    return user


def createUser(login_session):
    NewUser = User(name=login_session['username'],
                   email=login_session['email'],
                   picture=login_session['picture'])
    session.add(NewUser)
    session.commit()
    user = session.query(User).filter_by(email = login_session['email']).one()
    return user.id

""" routes to return data via json or xml apis """

@app.route('/expedition/<int:expedition_id>/xml')
def getExpeditionXML(expedition_id):
    expedition = session.query(Expedition).filter_by(id=expedition_id).one()
    root = Element('expedition', id=expedition.id)
    title = SubElement(root, 'title')
    description = SubElement(root, 'description')
    title.text = expedition.title
    description.text = expedition.description
    response = make_response('REST API')
    response.headers['Content-Type'] = 'application/xml'
    dump(expedition)


if __name__ == '__main__':
    app.secret_key = 'secret_shmecret'
    app.debug = True
    app.run(host='0.0.0.0', port=8080)

