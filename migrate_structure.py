import os
import shutil
from pathlib import Path

def migrate_project():
    base_dir = Path("d:/Code/elorza")
    
    print("🔄 Iniciando migración de estructura...")
    
    # 1. Crear nueva estructura backend
    new_backend = base_dir / "backend_clean"
    new_backend.mkdir(exist_ok=True)
    
    # 2. Crear estructura app
    app_dir = new_backend / "app"
    app_dir.mkdir(exist_ok=True)
    
    # 3. Copiar del backend existente que tiene mejor estructura
    source_backend = base_dir / "backend" / "app"
    if source_backend.exists():
        # Copiar modelos
        if (source_backend / "models").exists():
            shutil.copytree(source_backend / "models", app_dir / "models", dirs_exist_ok=True)
        
        # Copiar rutas
        if (source_backend / "routes").exists():
            shutil.copytree(source_backend / "routes", app_dir / "routes", dirs_exist_ok=True)
        
        # Copiar servicios
        if (source_backend / "services").exists():
            shutil.copytree(source_backend / "services", app_dir / "services", dirs_exist_ok=True)
            
        print("✅ Copiado código del backend")
    
    # 4. Crear __init__.py principal
    init_content = '''from flask import Flask, send_from_directory, render_template_string
from flask_cors import CORS
import os

def create_app():
    app = Flask(__name__, static_folder='../../frontend/dist')
    CORS(app)
    
    INDEX_HTML = """<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Sistema Gestión Agrícola - Elorza</title>
    <script type="module" crossorigin src="/assets/index.js"></script>
    <link rel="stylesheet" href="/assets/index.css">
</head>
<body>
    <div id="root"></div>
</body>
</html>"""
    
    @app.route('/')
    @app.route('/<path:path>')
    def serve_react(path=''):
        if path and os.path.exists(os.path.join(app.static_folder, path)):
            return send_from_directory(app.static_folder, path)
        return render_template_string(INDEX_HTML)
    
    return app
'''
    
    with open(app_dir / "__init__.py", "w", encoding="utf-8") as f:
        f.write(init_content)
    
    # 5. Crear run.py
    run_content = '''from app import create_app
import os

app = create_app()

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=False)
'''
    
    with open(new_backend / "run.py", "w", encoding="utf-8") as f:
        f.write(run_content)
    
    # 6. Copiar requirements
    req_source = base_dir / "backend" / "requirements.txt"
    if req_source.exists():
        shutil.copy2(req_source, new_backend / "requirements.txt")
    
    print("✅ Nueva estructura creada en backend_clean")
    print("🎉 Migración completada!")

if __name__ == "__main__":
    migrate_project()