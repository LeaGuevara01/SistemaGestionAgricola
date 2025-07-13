# sistema_gestion_agricola/utils/vite_helper.py
import json
import os
from flask import current_app, url_for

_manifest_cache = {}

def vite_asset(filename):
    env = current_app.config.get("ENV", "production")
    
    if env == "development":
        # En desarrollo, cargamos directo desde Vite dev server
        if filename.endswith(".js"):
            return f"http://localhost:5173/src/{filename}"
        else:
            return f"http://localhost:5173/{filename}"

    # En producción, buscamos el manifest.json
    manifest_path = os.path.join(current_app.root_path, 'static', 'dist', '.vite', 'manifest.json')


    if manifest_path not in _manifest_cache:
        with open(manifest_path, encoding='utf-8') as f:
            _manifest_cache[manifest_path] = json.load(f)

    manifest = _manifest_cache[manifest_path]

    if filename not in manifest:
        raise Exception(f"Asset '{filename}' no encontrado en manifest.json")

    entry = manifest[filename]
    assets = {
        "file": url_for('static', filename=f'dist/{entry["file"]}')
    }

    # Si hay css asociados, devolver la lista
    if "css" in entry:
        assets["css"] = [url_for('static', filename=f'dist/{css_file}') for css_file in entry["css"]]

    return assets
