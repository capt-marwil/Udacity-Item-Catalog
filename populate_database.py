from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from setup_database import Base, User, Expedition, Category, Item, expeditions_categories


engine = create_engine('sqlite:///catalog.db')
Base.metadata.bind = engine

DBSession = sessionmaker(bind=engine)
session = DBSession()


u = User(name='Robo Hiker',
         email='robo@robo.tv',
         picture='http://cdn.phys.org/newman/csz/news/800/2013/walkingrobot.jpg')


e = Expedition(title='Gros Mourne', description='''Gros Morne National Park is a world heritage site located on the west coast of Newfoundland. At 1,805 km2 (697 sq mi), it is the second largest national park in Atlantic Canada; it is surpassed by Torngat Mountains National Park, which is 9,700 km2 (3,700 sq mi). The park takes its name from Newfoundland's second-highest mountain peak (at 2,644 ft/806 m) located within the park.
Its French meaning is "large mountain standing alone," or more literally "great sombre." Gros Morne is a member of the Long Range Mountains, an outlying range of the Appalachian Mountains, stretching the length of the island's west coast. It is the eroded remnants of a mountain range formed 1.2 billion years ago. "The park provides a rare example of the process of continental drift, where deep ocean crust and the rocks of the earth's mantle lie exposed."[1]
The Gros Morne National Park Reserve was established in 1973, and was made a national park in October 1, 2005.''')

c = Category(name="Climbing",
             description="The step cliff of Western Brook Pond are up to 600 m (2000 ft) high and offer plenty of challenges for climbers",
             picture="img/climbing_bck.jpg",
             user_id=1)



e = session.query(Expedition).first()
c = session.query(Category).filter_by(name='Climbing').one()
e.category.append(c)
c.expedition.append(e)
session.add(e)
session.add(c)
session.commit()










