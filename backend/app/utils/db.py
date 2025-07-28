from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

def commit_or_rollback():
    """Utility function to commit or rollback database operations"""
    try:
        db.session.commit()
        return True
    except Exception as e:
        db.session.rollback()
        raise e