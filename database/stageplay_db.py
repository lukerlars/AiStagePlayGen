# This is just a template from grok:
# TODO adapt this for characters and add to application
#
from sqlalchemy import create_engine, Column, Integer, String, Float
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

# Create SQLite database engine
engine = create_engine('sqlite:///project.db', echo=True)

# Create a base class for declarative models
Base = declarative_base()

# Define Project model
class Project(Base):
    __tablename__ = 'projects'
    
    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)
    description = Column(String)
    budget = Column(Float)
    status = Column(String, default='active')

# Create database tables
Base.metadata.create_all(engine)

# Create a session factory
Session = sessionmaker(bind=engine)

def add_project(name, description=None, budget=0.0, status='active'):
    """Add a new project to the database."""
    session = Session()
    try:
        project = Project(name=name, description=description, budget=budget, status=status)
        session.add(project)
        session.commit()
        print(f"Added project: {name}")
    except Exception as e:
        session.rollback()
        print(f"Error adding project: {e}")
    finally:
        session.close()

def get_project(project_id):
    """Retrieve a project by ID."""
    session = Session()
    try:
        project = session.query(Project).filter_by(id=project_id).first()
        if project:
            return {
                'id': project.id,
                'name': project.name,
                'description': project.description,
                'budget': project.budget,
                'status': project.status
            }
        return None
    finally:
        session.close()

def update_project(project_id, **kwargs):
    """Update project details."""
    session = Session()
    try:
        project = session.query(Project).filter_by(id=project_id).first()
        if project:
            for key, value in kwargs.items():
                if hasattr(project, key):
                    setattr(project, key, value)
            session.commit()
            print(f"Updated project ID: {project_id}")
        else:
            print(f"Project ID {project_id} not found")
    except Exception as e:
        session.rollback()
        print(f"Error updating project: {e}")
    finally:
        session.close()

def delete_project(project_id):
    """Delete a project by ID."""
    session = Session()
    try:
        project = session.query(Project).filter_by(id=project_id).first()
        if project:
            session.delete(project)
            session.commit()
            print(f"Deleted project ID: {project_id}")
        else:
            print(f"Project ID {project_id} not found")
    except Exception as e:
        session.rollback()
        print(f"Error deleting project: {e}")
    finally:
        session.close()

# Example usage
if __name__ == "__main__":
    # Add some sample projects
    add_project("Website Redesign", "Redesign company website", 5000.0)
    add_project("Mobile App", "Develop new mobile application", 10000.0, "planned")
    
    # Retrieve a project
    project = get_project(1)
    if project:
        print(f"Retrieved project: {project}")
    
    # Update a project
    update_project(1, budget=7500.0, status="in_progress")
    
    # Delete a project
    delete_project(2)