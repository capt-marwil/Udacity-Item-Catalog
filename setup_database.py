from sqlalchemy import Table, Column, ForeignKey, Integer, String, Text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from sqlalchemy import create_engine


Base = declarative_base()

''' Table declaration '''
expeditions_categories = Table('expeditions_categories', Base.metadata,
                               Column('expedition_id', Integer,
                                      ForeignKey('expeditions.id'),
                                      primary_key=True),
                               Column('category_id', Integer,
                                      ForeignKey('categories.id'),
                                      primary_key=True)
                               )


class User(Base):
    __tablename__ = 'users'
    id = Column(Integer, primary_key=True)
    name = Column(String(80), nullable=False)
    email = Column(String(80), nullable=False)
    picture = Column(String(255), nullable=True)


class Expedition(Base):
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
            'category': self.category
        }


class Category(Base):
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
            'name': self.id,
            'description': self.id,
            'picture': self.id,
            'expedition': self.expedition
        }


class Item(Base):
    __tablename__ = 'items'
    id = Column(Integer, primary_key=True)
    name = Column(Integer, primary_key=True)
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


engine = create_engine('sqlite:///catalog.db')
Base.metadata.create_all(engine)
