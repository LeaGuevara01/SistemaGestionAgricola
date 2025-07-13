import os

EXCLUIR = {'venv', '__pycache__', 'node_modules', '.git', '.vscode', 'dist'}

def imprimir_estructura(base_dir, indent=0):
    for item in sorted(os.listdir(base_dir)):
        if item in EXCLUIR:
            continue
        path = os.path.join(base_dir, item)
        print('│   ' * indent + '├── ' + item)
        if os.path.isdir(path):
            imprimir_estructura(path, indent + 1)

# Ruta base (cambiá si hace falta)
directorio_raiz = 'D:/Code/elorza/sistema_gestion_agricola'
print(f"Estructura de: {directorio_raiz}")
imprimir_estructura(directorio_raiz)
