from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker

# Global registry for the engine and session
engine = None
db_session = None


def init_db(app):
    """Initialize SQLAlchemy engine and session tied to the flask app context"""
    global engine, db_session

    engine = create_engine(app.config["SQLALCHEMY_DATABASE_URI"])
    db_session = scoped_session(
        sessionmaker(autocommit=False, autoflush=False, bind=engine)
    )

    @app.teardown_appcontext
    def shutdown_session(exception=None):
        db_session.remove()