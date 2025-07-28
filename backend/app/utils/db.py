from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

def commit_or_rollback():
    """Helper para hacer commit o rollback automático"""
    try:
        db.session.commit()
        return True
    except Exception as e:
        db.session.rollback()
        raise e