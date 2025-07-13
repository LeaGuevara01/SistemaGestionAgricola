# run.py
from __init__ import create_app

app = create_app()
app.config['ENV'] = 'development'  # o 'production' en producción

if __name__ == '__main__':
    app.run(debug=True)
