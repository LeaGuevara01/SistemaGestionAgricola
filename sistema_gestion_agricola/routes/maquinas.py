# routes/maquinas.py
from flask import Blueprint, render_template, request, redirect, url_for, flash, current_app, request
from werkzeug.utils import secure_filename
from ..models import db, Maquina, Componente, MaquinaComponente, Frecuencia
from ..utils.files import allowed_file
import os

maquinas_bp = Blueprint('maquinas', __name__, url_prefix='/maquina')

# List Machines
@maquinas_bp.route('/')
def listar_maquinas():
    maquinas = Maquina.query.order_by(Maquina.Nombre).all()
    return render_template('maquinas/listar.html', maquinas=maquinas)

# Create Machine
@maquinas_bp.route('/agregar', methods=['GET', 'POST'])
def agregar_maquina():
    from werkzeug.utils import secure_filename
    from flask import current_app
    import os

    if request.method == 'POST':
        codigo = request.form['codigo']
        nombre = request.form['nombre']
        marca = request.form.get('marca')
        modelo = request.form.get('modelo')
        anio = request.form.get('anio')
        estado = request.form.get('estado')
        observaciones = request.form.get('observaciones')
        foto = request.files.get('foto')

        # Validar existencia código
        existe = Maquina.query.filter_by(Codigo=codigo).first()
        if existe:
            flash('Ya existe una máquina con ese código.')
            return redirect(url_for('maquinas.agregar_maquina'))

        foto_filename = None
        if foto and foto.filename != '':
            foto_filename = secure_filename(f"maquina_{codigo}.{foto.filename.rsplit('.', 1)[1].lower()}")
            ruta_foto = os.path.join(current_app.config['UPLOAD_FOLDER_MAQUINAS'], foto_filename)
            foto.save(ruta_foto)

        # Crear objeto máquina
        nueva_maquina = Maquina(
            Codigo=codigo,
            Nombre=nombre,
            Marca=marca,
            Modelo=modelo,
            Año=int(anio) if anio and anio.isdigit() else None,
            Estado=estado,
            Observaciones=observaciones,
            Foto=foto_filename
        )
        db.session.add(nueva_maquina)
        db.session.flush()  # Para obtener id antes de commit

        # Componentes seleccionados y frecuencias
        componentes_seleccionados = request.form.getlist('componentes_seleccionados')

        for id_componente_str in componentes_seleccionados:
            id_componente = int(id_componente_str)
            # Insertar relación máquina-componente
            assoc = MaquinaComponente(ID_Maquina=nueva_maquina.ID, ID_Componente=id_componente)
            db.session.add(assoc)

            frecuencia = request.form.get(f'frecuencia_{id_componente}')
            unidad = request.form.get(f'unidad_{id_componente}')
            criterio = request.form.get(f'criterio_{id_componente}')

            if frecuencia and frecuencia.isdigit() and int(frecuencia) > 0 and unidad:
                freq = Frecuencia(
                    ID_Maquina=nueva_maquina.ID,
                    ID_Componente=id_componente,
                    Frecuencia=int(frecuencia),
                    Unidad_tiempo=unidad,
                    Criterio_adicional=criterio
                )
                db.session.add(freq)

        try:
            db.session.commit()
            flash("Máquina registrada correctamente.")
            return redirect(url_for('maquinas.ver_maquina', id=nueva_maquina.ID))
        except Exception as e:
            db.session.rollback()
            flash(f'Error al guardar la máquina: {e}', 'error')
            return redirect(url_for('maquinas.agregar_maquina'))

    # GET
    componentes = Componente.query.all()
    return render_template('maquinas/agregar.html', componentes=componentes)

# Read Machine
@maquinas_bp.route('/<int:id>')
def ver_maquina(id):
    maquina = Maquina.query.get_or_404(id)

    from sqlalchemy.orm import aliased
    from sqlalchemy import select

    componentes_asociados = (
        db.session.query(
            Componente,
            Frecuencia.Frecuencia.label('frecuencia'),
            Frecuencia.Unidad_tiempo.label('unidad_tiempo'),
            Frecuencia.Criterio_adicional.label('criterio_adicional')
        )
        .join(MaquinaComponente, MaquinaComponente.ID_Componente == Componente.ID)
        .outerjoin(
            Frecuencia, 
            (Frecuencia.ID_Maquina == id) & (Frecuencia.ID_Componente == Componente.ID)
        )
        .filter(MaquinaComponente.ID_Maquina == id)
        .all()
    )

    subquery = select(MaquinaComponente.ID_Componente).filter(MaquinaComponente.ID_Maquina == id).scalar_subquery()
    componentes_no_asociados = Componente.query.filter(~Componente.ID.in_(subquery)).all()


    return render_template('maquinas/ver.html',
                           maquina=maquina,
                           componentes_asociados=componentes_asociados,
                           componentes_no_asociados=componentes_no_asociados)

# Update Machine
@maquinas_bp.route('/<int:id>/editar', methods=['GET', 'POST'])
def editar_maquina(id):
    maquina = Maquina.query.get(id)

    if not maquina:
        flash('Máquina no encontrada.', 'error')
        return redirect(url_for('maquinas.listar_maquinas'))

    if request.method == 'POST':
        nombre = request.form.get('nombre', '').strip()
        marca = request.form.get('marca', '').strip()
        modelo = request.form.get('modelo', '').strip()
        anio = request.form.get('anio', '').strip()
        estado = request.form.get('estado', '').strip()
        observaciones = request.form.get('observaciones', '').strip()
        foto = request.files.get('foto')

        if not nombre:
            flash('El nombre de la máquina es obligatorio.', 'error')
            return render_template('maquinas/editar.html', maquina=maquina)

        foto_filename = maquina.Foto
        filepath = None

        if foto and foto.filename != '':
            if allowed_file(foto.filename):
                # Eliminar foto anterior si existe
                if maquina.Foto and isinstance(maquina.Foto, str):
                    foto_anterior = os.path.join(current_app.config['UPLOAD_FOLDER_MAQUINAS'], maquina.Foto)
                    if os.path.isfile(foto_anterior):
                        try:
                            os.remove(foto_anterior)
                        except OSError as e:
                            print(f"No se pudo eliminar la foto anterior: {e}")
                # Guardar nueva foto
                extension = foto.filename.rsplit('.', 1)[1].lower()
                foto_filename = secure_filename(f"maquina_{id}.{extension}")
                filepath = os.path.join(current_app.config['UPLOAD_FOLDER_MAQUINAS'], foto_filename)
                foto.save(filepath)
            else:
                flash('Formato de imagen no válido. Use JPG, PNG o GIF.', 'error')
                return render_template('maquinas/editar.html', maquina=maquina)

        # Actualizar campos
        maquina.Nombre = nombre
        maquina.Marca = marca
        maquina.Modelo = modelo
        try:
            maquina.Año = int(anio)
        except ValueError:
            flash("Año inválido. Debe ser un número.", "error")
            return render_template('maquinas/editar.html', maquina=maquina)
        if estado != '':
            maquina.Estado = estado
        maquina.Observaciones = observaciones
        print("maquina.Foto antes:", maquina.Foto)
        print("Ruta absoluta de la imagen guardada:", filepath)
        print("Foto cargada:", foto.filename if foto else "No enviada")
        print("Archivo actual:", foto_filename)
        maquina.Foto = foto_filename

        try:
            db.session.commit()
            flash('Máquina actualizada correctamente.', 'success')
            return redirect(url_for('maquinas.ver_maquina', id=id))
        except Exception as e:
            db.session.rollback()
            flash(f'Error al actualizar: {str(e)}', 'error')
            return render_template('maquinas/editar.html', maquina=maquina)

    return render_template('maquinas/editar.html', maquina=maquina)

# Delete Machine
@maquinas_bp.route('/<int:id>/eliminar', methods=['POST'])
def eliminar_maquina(id):
    maquina = Maquina.query.get(id)
    if not maquina:
        flash("Máquina no encontrada.")
        return redirect(url_for('maquinas.listar_maquinas'))

    try:
        db.session.delete(maquina)
        db.session.commit()
        flash("Máquina eliminada correctamente.")
    except Exception as e:
        db.session.rollback()
        flash(f"Error al eliminar la máquina: {e}")

    return redirect(url_for('maquinas.listar_maquinas'))

# Create Component
@maquinas_bp.route('/<int:id_maquina>/asignar_componente', methods=['GET', 'POST'])
def asignar_componente(id_maquina):
    mensaje_error = None
    componentes = Componente.query.all()
    asociados = MaquinaComponente.query.filter_by(ID_Maquina=id_maquina).all()
    ids_asociados = {a.ID_Componente for a in asociados}

    if request.method == 'POST':
        id_componente = int(request.form['componente'])
        if id_componente in ids_asociados:
            mensaje_error = "Este componente ya está asignado a esta máquina."
        else:
            frecuencia = request.form['frecuencia']
            unidad = request.form['unidad_tiempo']
            criterio = request.form.get('criterio_adicional', '')

            nuevo_assoc = MaquinaComponente(ID_Maquina=id_maquina, ID_Componente=id_componente)
            db.session.add(nuevo_assoc)

            if frecuencia and unidad and frecuencia.isdigit() and int(frecuencia) > 0:
                freq = Frecuencia(
                    ID_Maquina=id_maquina,
                    ID_Componente=id_componente,
                    Frecuencia=int(frecuencia),
                    Unidad_tiempo=unidad,
                    Criterio_adicional=criterio
                )
                db.session.add(freq)

            try:
                db.session.commit()
                return redirect(url_for('maquinas.ver_maquina', id=id_maquina))
            except Exception as e:
                db.session.rollback()
                mensaje_error = f"Error al asignar componente: {e}"

    return render_template('maquinas/asignar_componente.html',
                           id_maquina=id_maquina, componentes=componentes, mensaje_error=mensaje_error)

# Edit Frequency
@maquinas_bp.route('/<int:id_maquina>/frecuencia/<int:id_componente>', methods=['GET', 'POST'])
def editar_frecuencia(id_maquina, id_componente):
    frecuencia = Frecuencia.query.filter_by(ID_Maquina=id_maquina, ID_Componente=id_componente).first()

    if request.method == 'POST':
        nueva_frecuencia = request.form['frecuencia']
        unidad_tiempo = request.form['unidad_tiempo']
        criterio_adicional = request.form.get('criterio_adicional', '')

        if frecuencia:
            frecuencia.Frecuencia = int(nueva_frecuencia) if nueva_frecuencia.isdigit() else None
            frecuencia.Unidad_tiempo = unidad_tiempo
            frecuencia.Criterio_adicional = criterio_adicional
        else:
            frecuencia = Frecuencia(
                ID_Maquina=id_maquina,
                ID_Componente=id_componente,
                Frecuencia=int(nueva_frecuencia) if nueva_frecuencia.isdigit() else None,
                Unidad_tiempo=unidad_tiempo,
                Criterio_adicional=criterio_adicional
            )
            db.session.add(frecuencia)

        try:
            db.session.commit()
            return redirect(url_for('maquinas.ver_maquina', id=id_maquina))
        except Exception as e:
            db.session.rollback()
            flash(f'Error al actualizar frecuencia: {e}', 'error')

    return render_template('maquinas/editar_frecuencia.html',
                           frecuencia=frecuencia, id_maquina=id_maquina, id_componente=id_componente)

# Create Photo
@maquinas_bp.route('/upload_foto/<int:id>', methods=['POST'])
def upload_foto_maquina(id):
    maquina = Maquina.query.get_or_404(id)

    if 'foto' not in request.files:
        flash('No se subió ninguna imagen.', 'error')
        return redirect(url_for('maquinas.ver_maquina', id=id))

    foto = request.files['foto']
    if foto.filename == '':
        flash('Archivo vacío.', 'error')
        return redirect(url_for('maquinas.ver_maquina', id=id))

    if foto and allowed_file(foto.filename):
        try:
            upload_folder = current_app.config['UPLOAD_FOLDER_MAQUINAS']
            os.makedirs(upload_folder, exist_ok=True)  # Asegura que exista la carpeta

            # Borrar foto anterior
            if maquina.Foto:
                foto_anterior = os.path.join(upload_folder, maquina.Foto)
                if os.path.exists(foto_anterior):
                    os.remove(foto_anterior)

            extension = foto.filename.rsplit('.', 1)[1].lower()
            filename = secure_filename(f"maquina_{id}.{extension}")
            filepath = os.path.join(upload_folder, filename)
            foto.save(filepath)

            maquina.Foto = filename
            db.session.commit()

            flash("Foto subida correctamente.", 'success')
        except Exception as e:
            db.session.rollback()
            current_app.logger.error(f"Error al subir la imagen: {e}")
            flash(f"Error al subir la imagen: {e}", 'error')
    else:
        flash("Formato de archivo no permitido. Solo JPG, JPEG, PNG, GIF.", 'error')

    return redirect(url_for('maquinas.ver_maquina', id=id))
