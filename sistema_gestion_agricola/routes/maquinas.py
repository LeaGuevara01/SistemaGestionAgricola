from flask import Blueprint, render_template, request, redirect, url_for, flash
from ..utils.db import get_db_connection
from ..utils.files import allowed_file

maquinas_bp = Blueprint('maquinas', __name__, url_prefix='/maquina')


# List Machines
@maquinas_bp.route('/')
def listar_maquinas():
    conn = get_db_connection()
    maquinas = conn.execute('SELECT * FROM maquinas').fetchall()
    conn.close()
    return render_template('maquinas/listar.html', maquinas=maquinas)

# Create Machine
@maquinas_bp.route('/agregar', methods=['GET', 'POST'])
def agregar_maquina():
    from werkzeug.utils import secure_filename
    from flask import current_app
    import os

    if request.method == 'POST':
        conn = get_db_connection()
        cursor = conn.cursor()

        # Datos de la máquina
        codigo = request.form['codigo']
        nombre = request.form['nombre']
        marca = request.form.get('marca')
        modelo = request.form.get('modelo')
        anio = request.form.get('anio')
        estado = request.form.get('estado')
        observaciones = request.form.get('observaciones')
        foto = request.files.get('foto')

        # Foto opcional
        foto_filename = None
        if foto and foto.filename != '':
            foto_filename = secure_filename(f"maquina_{codigo}.{foto.filename.rsplit('.', 1)[1].lower()}")
            ruta_foto = os.path.join(current_app.config['UPLOAD_FOLDER_MAQUINAS'], foto_filename)
            foto.save(ruta_foto)

        # Verificar si ya existe máquina con ese código
        ya_existe = cursor.execute('SELECT 1 FROM maquinas WHERE Codigo = ?', (codigo,)).fetchone()
        if ya_existe:
            flash('Ya existe una máquina con ese código.')
            conn.close()
            return redirect(url_for('maquinas.agregar_maquina'))

        # Insertar en la base
        cursor.execute('''
            INSERT INTO maquinas (Codigo, Nombre, Marca, Modelo, Año, Estado, Observaciones, Foto)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        ''', (codigo, nombre, marca, modelo, anio, estado, observaciones, foto_filename))
        id_maquina = cursor.lastrowid

        # Componentes seleccionados
        componentes_seleccionados = request.form.getlist('componentes_seleccionados')
        for id_componente in componentes_seleccionados:
            cursor.execute('''
                INSERT INTO maquinas_componentes (ID_Maquina, ID_Componente)
                VALUES (?, ?)
            ''', (id_maquina, id_componente))

            frecuencia = request.form.get(f'frecuencia_{id_componente}')
            unidad = request.form.get(f'unidad_{id_componente}')
            criterio = request.form.get(f'criterio_{id_componente}')

            if frecuencia and unidad and frecuencia.isdigit() and int(frecuencia) > 0:
                cursor.execute('''
                    INSERT INTO frecuencias (ID_Maquina, ID_Componente, Frecuencia, "Unidad tiempo", "Criterio adicional")
                    VALUES (?, ?, ?, ?, ?)
                ''', (id_maquina, id_componente, int(frecuencia), unidad, criterio))

        conn.commit()
        conn.close()

        flash("Máquina registrada correctamente.")
        return redirect(url_for('maquinas.ver_maquina', id=id_maquina))

    # Si es GET, obtener componentes y renderizar formulario
    conn = get_db_connection()
    componentes = conn.execute('SELECT * FROM componentes').fetchall()
    conn.close()
    return render_template('maquinas/agregar.html', componentes=componentes)


# Read Machine
@maquinas_bp.route('/<int:id>')
def ver_maquina(id):
    conn = get_db_connection()
    maquina = conn.execute('SELECT * FROM maquinas WHERE ID = ?', (id,)).fetchone()
    
    if not maquina:
        conn.close()
        flash("Máquina no encontrada.")
        return redirect(url_for('maquinas.listar_maquinas'))
    
    # Obtener componentes asociados a la máquina con sus frecuencias
    componentes_asociados = conn.execute('''
        SELECT c.*, f.Frecuencia, f."Unidad tiempo", f."Criterio adicional"
        FROM componentes c
        JOIN maquinas_componentes mc ON c.ID = mc.ID_Componente
        LEFT JOIN frecuencias f ON c.ID = f.ID_Componente AND mc.ID_Maquina = f.ID_Maquina
        WHERE mc.ID_Maquina = ?
    ''', (id,)).fetchall()

    # Componentes no asociados
    componentes_disponibles = conn.execute('''
        SELECT * FROM componentes
        WHERE ID NOT IN (
            SELECT ID_Componente FROM maquinas_componentes WHERE ID_Maquina = ?
        )
    ''', (id,)).fetchall()

    conn.close()
    return render_template('maquinas/ver.html', maquina=maquina,
        componentes_asociados=componentes_asociados,
        componentes_no_asociados=componentes_disponibles)


# Update Machine
@maquinas_bp.route('/<int:id>/editar', methods=['GET', 'POST'])
def editar_maquina(id):
    from werkzeug.utils import secure_filename
    from flask import current_app
    import os, sqlite3

    conn = get_db_connection()
    maquina = conn.execute('SELECT * FROM maquinas WHERE ID = ?', (id,)).fetchone()

    if not maquina:
        conn.close()
        flash('Máquina no encontrada.', 'error')
        return redirect(url_for('maquinas.listar_maquinas'))

    if request.method == 'POST':
        try:
            # Obtener datos del formulario
            nombre = request.form.get('nombre', '').strip()
            marca = request.form.get('marca', '').strip()
            modelo = request.form.get('modelo', '').strip()
            anio = request.form.get('anio', '').strip()
            estado = request.form.get('estado', '').strip()
            observaciones = request.form.get('observaciones', '').strip()
            foto = request.files.get('foto')

            # Validación
            if not nombre:
                flash('El nombre de la máquina es obligatorio.', 'error')
                conn.close()
                return render_template('maquinas/editar.html', maquina=maquina)

            # Procesar foto
            foto_filename = maquina['Foto']
            if foto and foto.filename != '':
                if allowed_file(foto.filename):
                    # Eliminar foto anterior si existe
                    if maquina['Foto']:
                        foto_anterior = os.path.join(current_app.config['UPLOAD_FOLDER_MAQUINAS'], maquina['Foto'])
                        if os.path.exists(foto_anterior):
                            try:
                                os.remove(foto_anterior)
                            except OSError:
                                pass
                    # Guardar nueva foto
                    extension = foto.filename.rsplit('.', 1)[1].lower()
                    foto_filename = secure_filename(f"maquina_{id}.{extension}")
                    filepath = os.path.join(current_app.config['UPLOAD_FOLDER_MAQUINAS'], foto_filename)
                    foto.save(filepath)
                else:
                    flash('Formato de imagen no válido. Use JPG, PNG o GIF.', 'error')
                    conn.close()
                    return render_template('maquinas/editar.html', maquina=maquina)

            # Actualizar en la base de datos
            conn.execute('''
                UPDATE maquinas SET 
                    Nombre = ?, 
                    Marca = ?, 
                    Modelo = ?, 
                    Año = ?, 
                    Estado = ?, 
                    Observaciones = ?, 
                    Foto = ?
                WHERE ID = ?
            ''', (nombre, marca, modelo, anio, estado, observaciones, foto_filename, id))

            conn.commit()
            flash('Máquina actualizada correctamente.', 'success')
            conn.close()
            return redirect(url_for('maquinas.ver_maquina', id=id))

        except sqlite3.Error as e:
            conn.rollback()
            flash(f'Error de base de datos: {str(e)}', 'error')
            conn.close()
            return render_template('maquinas/editar.html', maquina=maquina)

        except Exception as e:
            conn.rollback()
            flash(f'Error inesperado: {str(e)}', 'error')
            conn.close()
            return render_template('maquinas/editar.html', maquina=maquina)

    conn.close()
    return render_template('maquinas/editar.html', maquina=maquina)

# Delete Machine
@maquinas_bp.route('/<int:id>/eliminar', methods=['POST'])
def eliminar_maquina(id):
    conn = get_db_connection()
    maquina = conn.execute('SELECT * FROM maquinas WHERE ID = ?', (id,)).fetchone()

    if not maquina:
        conn.close()
        flash("Máquina no encontrada.")
        return redirect(url_for('maquinas.listar_maquinas'))

    conn.execute('DELETE FROM maquinas WHERE ID = ?', (id,))
    conn.commit()
    conn.close()

    flash("Máquina eliminada correctamente.")
    return redirect(url_for('maquinas.listar_maquinas'))

# Upload Machine Foto
@maquinas_bp.route('/upload_foto/<int:id>', methods=['POST'])
def upload_foto_maquina(id):
    from werkzeug.utils import secure_filename
    import os
    from flask import current_app

    if 'foto' not in request.files:
        flash('No se subió ninguna imagen.')
        return redirect(url_for('maquinas.ver_maquina', id=id))

    foto = request.files['foto']
    if foto.filename == '':
        flash('Archivo vacío.')
        return redirect(url_for('maquinas.ver_maquina', id=id))

    if foto and allowed_file(foto.filename):
        try:
            # Eliminar foto anterior si existe
            conn = get_db_connection()
            maquina = conn.execute('SELECT Foto FROM maquinas WHERE ID = ?', (id,)).fetchone()
            if maquina and maquina['Foto']:
                foto_anterior = os.path.join(current_app.config['UPLOAD_FOLDER_MAQUINAS'], maquina['Foto'])
                if os.path.exists(foto_anterior):
                    os.remove(foto_anterior)

            # Guardar nueva imagen
            extension = foto.filename.rsplit('.', 1)[1].lower()
            filename = secure_filename(f"maquina_{id}.{extension}")
            filepath = os.path.join(current_app.config['UPLOAD_FOLDER_MAQUINAS'], filename)
            foto.save(filepath)

            # Actualizar base de datos
            conn.execute('UPDATE maquinas SET Foto = ? WHERE ID = ?', (filename, id))
            conn.commit()
            conn.close()

            flash("Foto subida correctamente.")
        except Exception as e:
            flash(f"Error al subir la imagen: {e}")
    else:
        flash("Formato de archivo no permitido. Solo JPG, PNG, GIF.")

    return redirect(url_for('maquinas.ver_maquina', id=id))

# Frequency Management

# Assign Component to Machine
@maquinas_bp.route('/<int:id_maquina>/asignar_componente', methods=['GET', 'POST'])
def asignar_componente(id_maquina):
    conn = get_db_connection()
    mensaje_error = None
    try:
        componentes = conn.execute('SELECT * FROM componentes').fetchall()
        # Obtener componentes asociados a la máquina
        asociados = conn.execute('''
            SELECT ID_Componente FROM maquinas_componentes
            WHERE ID_Maquina = ?
        ''', (id_maquina,)).fetchall()
        # Convertir a un set para verificar rápidamente
        ids_asociados = {a['ID_Componente'] for a in asociados}
        # Si el método es POST, procesar la asignación
        if request.method == 'POST':
            id_componente = int(request.form['componente'])
            # Verificar si el componente ya está asociado a la máquina
            if id_componente in ids_asociados:
                mensaje_error = "Este componente ya está asignado a esta máquina."
            else:
                frecuencia = request.form['frecuencia']
                unidad = request.form['unidad_tiempo']
                criterio = request.form.get('criterio_adicional', '')
                # Insertar el componente en la relación muchos a muchos
                conn.execute('''
                    INSERT INTO maquinas_componentes (ID_Maquina, ID_Componente)
                    VALUES (?, ?)
                ''', (id_maquina, id_componente))
                # Insertar la frecuencia si es válida
                if frecuencia and unidad and frecuencia.isdigit() and int(frecuencia) > 0:
                    conn.execute('''
                        INSERT INTO frecuencias (ID_Maquina, ID_Componente, Frecuencia, "Unidad tiempo", "Criterio adicional")
                        VALUES (?, ?, ?, ?, ?)
                    ''', (id_maquina, id_componente, int(frecuencia), unidad, criterio))
                # Confirmar cambios
                conn.commit()
                # Redirigir a la vista de la máquina
                return redirect(url_for('maquinas.ver_maquina', id=id_maquina))
    finally:
        # Cerrar la conexión a la base de datos
        conn.close()
    # Si es GET, mostrar el formulario
    return render_template('maquinas/asignar_componente.html', id_maquina=id_maquina, componentes=componentes, mensaje_error=mensaje_error)


# Frequency Editing
@maquinas_bp.route('/<int:id_maquina>/frecuencia/<int:id_componente>', methods=['GET', 'POST'])
def editar_frecuencia(id_maquina, id_componente):
    conn = get_db_connection()
    
    # Obtener frecuencia actual si existe
    frecuencia = conn.execute('''
        SELECT * FROM frecuencias WHERE ID_Maquina = ? AND ID_Componente = ?
    ''', (id_maquina, id_componente)).fetchone()
    
    if request.method == 'POST':
        nueva_frecuencia = request.form['frecuencia']
        unidad_tiempo = request.form['unidad_tiempo']
        criterio_adicional = request.form.get('criterio_adicional', '')

        cursor = conn.cursor()

        if frecuencia:
            # Actualizar registro existente
            cursor.execute('''
                UPDATE frecuencias
                SET Frecuencia = ?, "Unidad tiempo" = ?, "Criterio adicional" = ?
                WHERE ID_Maquina = ? AND ID_Componente = ?
            ''', (nueva_frecuencia, unidad_tiempo, criterio_adicional, id_maquina, id_componente))
        else:
            # Insertar nuevo registro
            cursor.execute('''
                INSERT INTO frecuencias (ID_Maquina, ID_Componente, Frecuencia, "Unidad tiempo", "Criterio adicional")
                VALUES (?, ?, ?, ?, ?)
            ''', (id_maquina, id_componente, nueva_frecuencia, unidad_tiempo, criterio_adicional))
        
        # Redirigir a la vista de la máquina
        conn.commit()
        conn.close()
        return redirect(url_for('maquinas.ver_maquina', id=id_maquina))
    
    conn.close()
    return render_template('maquinas/editar_frecuencia.html', frecuencia=frecuencia, id_maquina=id_maquina, id_componente=id_componente)
