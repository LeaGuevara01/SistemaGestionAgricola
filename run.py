# /run.py
from sistema_gestion_agricola import create_app
from sistema_gestion_agricola.models import db
app = create_app()

app.config['ENV'] = 'production'