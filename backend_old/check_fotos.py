from app import create_app
from app.models.componente import Componente

app = create_app()
with app.app_context():
    componentes = Componente.query.limit(10).all()
    print("📸 Datos de fotos en BD:")
    for c in componentes:
        foto = getattr(c, 'Foto', None)
        print(f"ID: {c.id}, Nombre: {c.nombre}, Foto: {foto}")
