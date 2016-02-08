#Project: P3 Item Catalog#
A python application to create expeditions and create categories for 
activities users want to pursue. The items needed on the expedition can be 
added to the categories.
Users can only edit or delete those expeditions, categories and items they 
created.


##Requierements##
to run this project requires python 2.7.x 

###Python Modules requiered###
* Flask http://flask.pocoo.org/
* sqlalchemy, sqlalchemy.orm http://www.sqlalchemy.org/
* Flask SeaSurf https://flask-seasurf.readthedocs.org/en/latest/
* setup_database local module that defines the sqlite database schema
* oauth2client.client https://github.com/google/oauth2client
* httplib2 https://github.com/jcgregorio/httplib2
* json https://docs.python.org/2/library/json.html
* requests http://docs.python-requests.org/en/master/
* random https://docs.python.org/2/library/random.html
* string https://docs.python.org/2/library/string.html
* xml.etree.ElementTree https://docs.python.org/2/library/xml.etree.elementtree.html

###Other Software:###
* SQLite (but any other relational Database can be used for data storage)
* bootstrap 3.x
* jquery- 2.x

##Project Structure##
```
project
|
|---static
|   |
|   |-bootstrap.css
|   |-bootstrap.js
|   |-bootstrap.min.css
|   |-bootstrap.min.js
|   |-bootstrap-theme.css
|   |-bootstrap-theme.min.css
|   |-ie10-viewport-bug-workaround.css
|   |-ie10-viewport-bug-workaround.js
|   |-jquey-2.2.0.min.js
|   |-jumbotron-narrow.css
|   |-img
|       |-title_index.jpg
|
|---templates
|       |
|       |-addCategory.html
|       |-addExpedition.html
|       |-addItem.html
|       |-base.html
|       |-category.html
|       |-deleteCategory.html
|       |-deleteExpedition.html
|       |-deleteItem.html
|       |-editCategory.html
|       |-editExpedition.html
|       |-editItem.html
|       |-expedition.html
|       |-index.html
|       |-item.html
|       |-login.html
|       |-public_expedition.html
|       |-public_index.html
|
|-client_secrets.json
|-fb_client_secrets.json
|-main.py
|-README.md
|-setupdatabase.py``


##Installation##
* Download the zip File and unpack it into a directory using your favorite 
unzipper e.g. `unzip project.zip` 
* Alternatively clone the repo from [github](https://github.com/capt-marwil/project)
 by typing `git clone https://github.com/capt-marwil/project/`
* To set up the database run setup_database.py. This will create an empty sqlite
file in the /project named catalog.db
* Currently main.py is configured to run with a vm container like vagrant
* If you plan to run the app on your physical computer it might be nessecary
to change the servers address in main.py
* on the command line change into the `project` directory and type `python main.py`
on the command prompt. If any python modules are missed the program will complain 
and tell what modules are missing. The links to the instructions how to install
the missing modules are included above.
* To start creating an expedition and to add categories an items go to 
http://localhost:8080/ 
* Navigate to http://localhost:808/ to login and login-in 
with either your google account or your facebook credentials and start
 adding expeditions, categories for activities and items needed 
 for the activities.


##Miscelleanous##
* Added the possibility to add, edit and delete images to every expedition,
 category and item
* Added protection against csrf attacks by using the Flask Seasurf extension
* Implemented additional API endpoints for XML 
* I added an additional tier to the original database schema (Table expeditions)
* Expeditions and Categories are linked via a linking table (expeditions_categories)
  to map a many to many relationship.
* Added basic protection against the insertion of duplicate expeditions, 
categories or items
* With the current data model it is possible for the owner of an expedition to
 delete the expedition with all categories and items even if he isn't the owner
 of the categories and items. I wanted to ensure that the creation of the activites
 and items can be a collaborative project and users can add categories and items
  to expeditions they don't own.
 

##Additional Notes##
* I discovered halfway through the project that Expal already is an registered
trademark. https://www.maxam.net/en/expal/about_us/who_we_are 
Nevertheless I decided to keep the name as I don't use the name
 commercially and never intend to so. I hope this doesn't violate any
 udacity rules. If so I will change the name.
 
* The image used for the starting page was taken from here and is in the public
domain. The image and copyright notes can be found here:
http://images.google.de/imgres?imgurl=https%3A%2F%2Fcynthiajunelong.files.wordpress.com%2F2014%2F01%2Fglimpse_of_the_endurance_shackleton_expedition_1914-17_hurley_a090018.jpg&imgrefurl=https%3A%2F%2Fcynthiajunelong.wordpress.com%2Ftag%2Fsir-ernest-shackleton%2F&h=1100&w=1500&tbnid=TZreYe2jLDNTaM%3A&docid=tyL2ODXLLvNbIM&ei=IXq3VpeONoP6PIfLuLgC&tbm=isch&iact=rc&uact=3&dur=1934&page=2&start=51&ndsp=55&ved=0ahUKEwjXot6akubKAhUDPQ8KHYclDicQrQMIigIwTA

* There seems to be a problem with logging out of the application when the user
has been logged in for a longer time > 30 min and didn't interact with the app.
Only solution I could find was to delete cookies and reload the app. From the
information I gathered it seems to be the case that the session runs out and I
didn't find a way to keep it alive, without user interaction.
