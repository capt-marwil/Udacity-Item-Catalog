from sqlalchemy import Table, Column, ForeignKey, Integer, String, Text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from sqlalchemy import create_engine
from xml.etree.ElementTree import Element, SubElement

Base = declarative_base()

""" Table declaration """
""" create a many to many relationship between expeditions and categories """
expeditions_categories = Table('expeditions_categories', Base.metadata,
                               Column('expedition_id', Integer,
                                      ForeignKey('expeditions.id'),
                                      primary_key=True),
                               Column('category_id', Integer,
                                      ForeignKey('categories.id'),
                                      primary_key=True)
                               )



class User(Base):
    """ stores basic user information """
    __tablename__ = 'users'
    id = Column(Integer, primary_key=True)
    name = Column(String(80), nullable=False)
    email = Column(String(80), nullable=False)
    picture = Column(String(255), nullable=True)


class Expedition(Base):
    """
    stores information about an expedition
    uses user_id as a foreign key to keep track of ownership
    category as a one to many relationship to expedition_categories
    """
    __tablename__ = 'expeditions'
    id = Column(Integer, primary_key=True)
    title = Column(String(80), nullable=False)
    description = Column(Text, nullable=True)
    picture = Column(String(255))
    user_id = Column(Integer, ForeignKey('users.id'))
    user = relationship(User)
    category = relationship('Category', secondary=expeditions_categories,
                            back_populates='expedition')

    @property
    def serialize_json(self):
        return {
            'id': self.id,
            'title': self.title,
            'description': self.description,
        }


class Category(Base):
    """
    stores information about categories/activites
    uses user_id as a foreign key to keep track of ownership
    expedition as a one to many relationship to expedition_categories
    """
    __tablename__ = 'categories'
    id = Column(Integer, primary_key=True)
    name = Column(String(80), nullable=False)
    description = Column(String(255), nullable=False)
    picture = Column(String(255), nullable=True)
    user_id = Column(Integer, ForeignKey('users.id'))
    expedition = relationship('Expedition',
                              secondary=expeditions_categories,
                              back_populates='category')

    @property
    def serialize_json(self):
        return {
            'id': self.id,
            'name': self.name,
            'description': self.description,
            'picture': self.picture,
        }


class Item(Base):
    """
    stores the items associated with an certain category and expedition
    uses user_id to keep track of ownership
    """
    __tablename__ = 'items'
    id = Column(Integer, primary_key=True)
    name = Column(String(100), nullable=False)
    description = Column(String(255), nullable=False)
    picture = Column(String(255), nullable=True)
    user_id = Column(Integer, ForeignKey('users.id'))
    category_id = Column(Integer, ForeignKey('categories.id'))
    expedition_id = Column(Integer, ForeignKey('expeditions.id'))
    category = relationship(Category)
    expedition = relationship(Expedition)

    @property
    def serialize_json(self):
        return {
            'id': self.id,
            'name': self.name,
            'description': self.name,
            'picture': self.picture,
            'category_id': self.category_id,
            'expedition_id': self.expedition_id
        }

""" Create the sqllite database """
engine = create_engine('sqlite:///catalog.db')
Base.metadata.create_all(engine)