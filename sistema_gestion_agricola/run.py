# sistema_gestion_agricola/run.py
from sistema_gestion_agricola import create_app
from sistema_gestion_agricola.models import db
import os

app = create_app()

app.config['ENV'] = 'development'

if __name__ == '__main__':
    app.run(debug=True)
