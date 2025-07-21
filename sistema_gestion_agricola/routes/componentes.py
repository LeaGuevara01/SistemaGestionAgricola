# routes/componente.py
from flask import Blueprint, request, redirect, url_for, render_template, flash, current_app
from werkzeug.utils import secure_filename
import os
from ..models import db, Componente, Proveedor, ComponentesProveedores, MaquinaComponente, Frecuencia, Stock
from ..utils.files import allowed_file
from ..utils.stock_utils import obtener_stock_actual

componentes_bp = Blueprint('componentes', __name__, url_prefix='/componente')


@componentes_bp.route('/')
def lista_componentes():
    componentes = Componente.query.all()
    return render_template('componentes/listar.html', componentes=componentes)

# Create Component
@componentes_bp.route('/agregar', methods=['GET', 'POST'])
def registrar_componente():
    if request.method == 'POST':
        codigo = request.form.get('codigo')
        nombre = request.form.get('nombre')
        descripcion = request.form.get('descripcion', '')
        tipo = request.form.get('tipo', '')
        marca = request.form.get('marca', '')
        modelo = request.form.get('modelo', '')
        precio_str = request.form.get('precio', '0')
        foto = request.files.get('foto')
        proveedores_ids = request.form.getlist('proveedores_seleccionados')

        foto_filename = None
        if foto and foto.filename != '':
            foto_filename = secure_filename(foto.filename)
            ruta = os.path.join(current_app.config['UPLOAD_FOLDER_COMPONENTES'], foto_filename)
            foto.save(ruta)

        try:
            precio = float(precio_str)
        except ValueError:
            precio = 0

        nuevo_componente = Componente(
            ID_Componente=codigo,
            Nombre=nombre,
            Descripcion=descripcion,
            Tipo=tipo,
            Foto=foto_filename,
            Marca=marca,
            Modelo=modelo,
            Precio=precio
        )
        db.session.add(nuevo_componente)
        db.session.flush()  # Para obtener el ID

        for id_proveedor in proveedores_ids:
            relacion = ComponentesProveedores(ID_Proveedor=int(id_proveedor), ID_Componente=nuevo_componente.ID)
            db.session.add(relacion)

        try:
            db.session.commit()
            flash(f'Componente "{nombre}" agregado con éxito.')
            return redirect(url_for('componentes.vista_componente', id=nuevo_componente.ID))
        except Exception as e:
            db.session.rollback()
            flash(f'Error al guardar componente: {e}', 'error')

    proveedores = Proveedor.query.all()
    return render_template('componentes/agregar.html', proveedores=proveedores)

# Read Component
@componentes_bp.route('/<int:id>')
def vista_componente(id):
    componente = Componente.query.get(id)
    if not componente:
        return render_template('404.html', message="Componente no encontrado"), 404

    stock_data = obtener_stock_actual()
    stock_actual = next((c['Stock_Actual'] for c in stock_data if c['ID'] == id), 0)

    proveedores = (
        Proveedor.query
        .join(ComponentesProveedores, Proveedor.ID == ComponentesProveedores.ID_Proveedor)
        .filter(ComponentesProveedores.ID_Componente == componente.ID)
        .all()
    )

    id_maquina = request.args.get('id_maquina')

    return render_template('componentes/ver.html', componente=componente, stock_actual=stock_actual, proveedores=proveedores, id_maquina=id_maquina)

# Update Component
@componentes_bp.route('/<int:id>/editar', methods=['GET', 'POST'])
def editar_componente(id):
    componente = Componente.query.get(id)
    if not componente:
        flash('Componente no encontrado.', 'error')
        return redirect(url_for('componentes.lista_componentes'))

    if request.method == 'POST':
        codigo = request.form.get('codigo', '').strip()
        nombre = request.form.get('nombre', '').strip()
        tipo = request.form.get('tipo', '').strip()
        marca = request.form.get('marca', '').strip()
        modelo = request.form.get('modelo', '').strip()
        precio_str = request.form.get('precio', '').strip()
        descripcion = request.form.get('descripcion', '').strip()
        foto = request.files.get('foto')

        if not nombre:
            flash('El nombre del componente es obligatorio.', 'error')
            return render_template('componentes/editar.html', componente=componente)

        try:
            precio_valor = float(precio_str) if precio_str else None
        except ValueError:
            flash('El precio debe ser un número válido.', 'error')
            return render_template('componentes/editar.html', componente=componente)

        foto_filename = componente.Foto
        if foto and foto.filename != '':
            if allowed_file(foto.filename):
                if componente.Foto:
                    foto_anterior = os.path.join(current_app.config['UPLOAD_FOLDER_COMPONENTES'], componente.Foto)
                    if os.path.exists(foto_anterior):
                        try:
                            os.remove(foto_anterior)
                        except OSError:
                            pass

                extension = foto.filename.rsplit('.', 1)[1].lower()
                foto_filename = secure_filename(f"componente_{id}.{extension}")
                filepath = os.path.join(current_app.config['UPLOAD_FOLDER_COMPONENTES'], foto_filename)
                foto.save(filepath)
            else:
                flash('Formato de imagen no válido. Use JPG, PNG o GIF.', 'error')
                return render_template('componentes/editar.html', componente=componente, tipos=tipos)

        componente.ID_Componente = codigo or None
        componente.Nombre = nombre
        componente.Tipo = tipo or None
        print(f"Guardando tipo: {componente.Tipo}")

        componente.Descripcion = descripcion or None
        componente.Foto = foto_filename
        componente.Marca = marca or None
        componente.Modelo = modelo or None
        componente.Precio = precio_valor

        try:
            db.session.commit()
            flash('Componente actualizado correctamente.', 'success')
            return redirect(url_for('componentes.vista_componente', id=id))
        except Exception as e:
            db.session.rollback()
            flash(f'Error al actualizar componente: {e}', 'error')
            return render_template('componentes/editar.html', componente=componente, tipos=tipos)

    tipos_existentes = db.session.query(Componente.Tipo).distinct().filter(Componente.Tipo.isnot(None)).all()
    tipos = sorted({tipo[0] for tipo in tipos_existentes if tipo[0]})

    return render_template('componentes/editar.html', componente=componente, tipos=tipos)

# Delete Component
@componentes_bp.route('/<int:id>/eliminar', methods=['POST'])
def eliminar_componente(id):
    componente = Componente.query.get(id)
    if not componente:
        flash('Componente no encontrado.', 'error')
        return redirect(url_for('componentes.lista_componentes'))

    try:
        if componente.Foto:
            foto_path = os.path.join(current_app.config['UPLOAD_FOLDER_COMPONENTES'], componente.Foto)
            if os.path.exists(foto_path):
                try:
                    os.remove(foto_path)
                except OSError:
                    pass

        # Relaciones
        MaquinaComponente.query.filter_by(ID_Componente=id).delete()
        Frecuencia.query.filter_by(ID_Componente=id).delete()
        ComponentesProveedores.query.filter_by(ID_Componente=id).delete()
        Stock.query.filter_by(ID_Componente=componente.ID_Componente).delete()

        db.session.delete(componente)
        db.session.commit()

        flash(f'Componente "{componente.Nombre}" eliminado correctamente.', 'success')
    except Exception as e:
        db.session.rollback()
        flash(f'Error al eliminar el componente: {e}', 'error')

    return redirect(url_for('componentes.lista_componentes'))

# Create Photo
@componentes_bp.route('/<int:id>/upload_foto', methods=['POST'])
def upload_foto_componente(id):
    componente = Componente.query.get(id)
    if not componente:
        flash('Componente no encontrado.')
        return redirect(url_for('componentes.lista_componentes'))

    if 'foto' not in request.files:
        flash('No se encontró archivo en el formulario.')
        return redirect(url_for('componentes.vista_componente', id=id))

    foto = request.files['foto']
    if foto.filename == '':
        flash('Archivo vacío.')
        return redirect(url_for('componentes.vista_componente', id=id))

    if foto and allowed_file(foto.filename):
        try:
            upload_folder = current_app.config['UPLOAD_FOLDER_COMPONENTES']
            os.makedirs(upload_folder, exist_ok=True)

            # Eliminar foto anterior si existe
            if componente.Foto:
                foto_anterior = os.path.join(upload_folder, componente.Foto)
                if os.path.exists(foto_anterior):
                    os.remove(foto_anterior)

            extension = foto.filename.rsplit('.', 1)[1].lower()
            filename = secure_filename(f"componente_{id}.{extension}")
            filepath = os.path.join(upload_folder, filename)
            foto.save(filepath)

            componente.Foto = filename
            db.session.commit()
            flash("Foto del componente actualizada.")
        except Exception as e:
            db.session.rollback()
            flash(f"Error al actualizar la foto: {e}", 'error')
    else:
        flash("Formato de archivo no permitido. Solo JPG, JPEG, PNG, GIF.")

    return redirect(url_for('componentes.vista_componente', id=id))