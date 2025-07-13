# run.py
from sistema_gestion_agricola import create_app

app = create_app()

if __name__ == '__main__':
    app.run(debug=True)
