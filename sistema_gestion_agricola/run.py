# run.py
from sistema_gestion_agricola import create_app # 'from .' @root/sistema_gestion_agricola/run.py && __init__.py => python -m sistema_gestion_agricola.run
                                # 'from __init__' @root/sistema_gestion_agricola/run.py && __init__.py => gunicorn run_app
                                # 'from sistema_gestion_agricola' @root/run.py/sistema_gestion_agricola && __init__.py => python -m sistema_gestion_agricola.run

app = create_app()
app.config['ENV'] = 'development'  # o 'production' en producción

if __name__ == '__main__':
    app.run(debug=True)
