# run.py
from sistema_gestion_agricola import create_app
from sistema_gestion_agricola.models import db

app = create_app()

app.config['ENV'] = 'development'  # o 'production' en producción

if __name__ == '__main__':
    app.run(debug=True)
