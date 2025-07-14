# run.py
from sistema_gestion_agricola.__init__ import create_app

app = create_app()
app.config['ENV'] = 'production'  # 'production' o 'development'

if __name__ == '__main__':
    app.run(debug=False)
