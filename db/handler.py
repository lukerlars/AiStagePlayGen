# This is just a template from grok:
# TODO adapt this for characters and add to application
#
from sqlalchemy import create_engine, Column, Integer, String 
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy.inspection import inspect

# Create SQLite database engine
engine = create_engine('sqlite:///db/stageplay/state.db', echo = False) 

# Create a base class for declarative models
Base = declarative_base()

class Character(Base):
    __tablename__ = 'character' 

    name = Column(String, nullable=False, primary_key=True)
    gender = Column(String, nullable= False)
    age = Column(Integer)
    disposition = Column(String)
    
class Relationships(Base):
    __tablename__ = 'relationships'
    id = Column(Integer, primary_key= True, autoincrement= True)
    character = Column(String, nullable= False)
    recipient_character = Column(String, nullable= False)
    relationship = Column(String)

# Create database tables
Base.metadata.create_all(engine)

# Create a session factory
Session = sessionmaker(bind=engine)


def add_entry(entry : Character | Relationships):
    """Add a new project to the database."""
    session = Session()
    try:
        session.add(entry)
        session.commit()
    except Exception as e:
        session.rollback()
        print(f"Error adding entry: {e}")
    finally:
        session.close()


def get_character(character_name):
    """Retrieve a character"""
    session = Session()
    try:
        character = session.query(Character).filter_by(name=character_name).first()
        if character:
            return {
                'name': character.name,
                'gender': character.gender,
                'age': character.age,
                'disposition': character.disposition
            }
        return None
    finally:
        session.close()


def get_character_relationships(character_name):
    """Retrieve all relationships for a character"""
    session = Session()
    try:
        relationships = session.query(Relationships).filter_by(character=character_name).all()
        if relationships:
            return {rel.recipient_character: rel.relationship for rel in relationships}
        return None
    finally:
        session.close()


def get_roster():
    """Gets all characters and their relationships"""

    with Session() as session:
        character_cols = [i.key for i in inspect(Character).attrs]
        character_query = session.query(Character).all()

        # Get list of characters 
        characters = [{col: getattr(res, col) for col in character_cols} 
                    for res in character_query
                    ]

        # For each character append stored relationships 
        for character in characters:
            relation_query = (session
                            .query(Relationships)
                            .filter_by(character = character["name"])
                            .all()
                            )
            character["relationships"] = []
            for relation in relation_query:
                character["relationships"].append(
                    {relation.recipient_character : relation.relationship}
                )
    return characters




def update_character(character_name, **kwargs):
    """Update project details."""
    session = Session()
    try:
        character = session.query(Character).filter_by(name = character_name).first()
        if character:
            for key, value in kwargs.items():
                if hasattr(character, key):
                    setattr(character, key, value)
            session.commit()
            print(f"Updated character: {character_name}")
        else:
            print(f"Character {character} not found")
    except Exception as e:
        session.rollback()
        print(f"Error updating character: {e}")
    finally:
        session.close()

def delete_character(character_name):
    """Delete a characters by ID."""
    session = Session()
    try:
        character = session.query(Character).filter_by(name = character_name).first()
        if character:
            session.delete(character)
            session.commit()
            print(f"Deleted character: {character}")
        else: 
            print(f"Character {character} not found")
    except Exception as e:
        session.rollback()
        print(f"Error deleting character: {e}")
    finally:
        session.close()
