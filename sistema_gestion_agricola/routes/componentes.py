# routes/componentes.py
from flask import Blueprint, request, redirect, url_for, render_template, flash, current_app
from werkzeug.utils import secure_filename
import os
import sqlite3
from ..utils.db import get_db_connection
from ..utils.files import allowed_file
from ..utils.stock_utils import obtener_stock_actual


componentes_bp = Blueprint('componentes', __name__, url_prefix='/componente')


# Component Management

# List Components
@componentes_bp.route('/')
def lista_componentes():
    conn = get_db_connection()
    componentes = conn.execute('SELECT * FROM componentes').fetchall()
    conn.close()
    return render_template('componentes/listar.html', componentes=componentes)


# Component Registration
# This route allows users to register a new component with its details and photo.
@componentes_bp.route('/agregar', methods=['GET', 'POST'])
def registrar_componente():

    # If the request is POST, process the form data
    if request.method == 'POST':
        codigo = request.form.get('codigo')
        nombre = request.form['nombre']
        descripcion = request.form['descripcion']
        tipo = request.form['tipo']
        foto = request.files.get('foto')

        foto_filename = None
        if foto and foto.filename != '':
            foto_filename = secure_filename(foto.filename)
            ruta = os.path.join(current_app.config['UPLOAD_FOLDER_COMPONENTES'], foto_filename)
            foto.save(ruta)

        # Guardar en base de datos
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute('''INSERT INTO componentes (ID_Componente, Nombre, Descripcion, Tipo, Foto) VALUES (?, ?, ?, ?, ?)''', (codigo, nombre, descripcion, tipo, foto_filename))
        nuevo_id = cursor.lastrowid
        conn.commit()
        conn.close()
        return redirect(url_for('componentes.vista_componente', id=nuevo_id))
    # If the request is GET, render the form
    return render_template('componentes/registrar.html')


# Component Details
# This route allows users to view the details of a specific component, including its suppliers and frequencies
@componentes_bp.route('/<int:id>')
def vista_componente(id):
    conn = get_db_connection()
    componente = conn.execute('SELECT * FROM componentes WHERE ID = ?', (id,)).fetchone()
    id_maquina = request.args.get('id_maquina')

    if componente is None:
        conn.close()
        return render_template('404.html', message="Componente no encontrado"), 404

    # Obtener stock total de todos los componentes
    stock_data = obtener_stock_actual()

    # Buscar el stock del componente actual
    stock_actual = next((c['Stock_Actual'] for c in stock_data if c['ID'] == id), 0)

    # Obtener proveedores asociados
    proveedores = conn.execute('''
        SELECT p.*
        FROM proveedores p
        JOIN componentes_proveedores cp ON p.ID = cp.ID_Proveedor
        WHERE cp.ID_Componente = ?
    ''', (componente['ID'],)).fetchall()

    conn.close()
    return render_template('componentes/ver.html', componente=componente, stock_actual=stock_actual, proveedores=proveedores, id_maquina=id_maquina)


# Update Component
@componentes_bp.route('/<int:id>/editar', methods=['GET', 'POST'])
def editar_componente(id):

    conn = get_db_connection()
    
    # Obtener el componente
    componente = conn.execute('SELECT * FROM componentes WHERE ID = ?', (id,)).fetchone()
    
    if not componente:
        conn.close()
        flash('Componente no encontrado.', 'error')
        return redirect(url_for('componentes.lista_componentes'))


    if request.method == 'POST':
        try:
            # Obtener datos del formulario
            codigo = request.form.get('codigo', '').strip()
            nombre = request.form.get('nombre', '').strip()
            tipo = request.form.get('tipo', '').strip()
            marca = request.form.get('marca', '').strip()
            modelo = request.form.get('modelo', '').strip()
            precio_str = request.form.get('precio', '').strip()
            descripcion = request.form.get('descripcion', '').strip()
            foto = request.files.get('foto')

            # Validación
            if not nombre:
                flash('El nombre del componente es obligatorio.', 'error')
                conn.close()
                return render_template('componentes/editar.html', componente=componente)


            # Procesar precio
            precio_valor = None
            if precio_str:
                try:
                    precio_valor = float(precio_str)
                except ValueError:
                    flash('El precio debe ser un número válido.', 'error')
                    conn.close()
                    return render_template('componentes/editar.html', componente=componente)


            # Procesar foto
            foto_filename = componente['Foto']
            if foto and foto.filename != '':
                if allowed_file(foto.filename):
                    # Eliminar foto anterior
                    if componente['Foto']:
                        foto_anterior = os.path.join(current_app.config['UPLOAD_FOLDER_COMPONENTES'], componente['Foto'])
                        if os.path.exists(foto_anterior):
                            try:
                                os.remove(foto_anterior)
                            except OSError:
                                pass
                    
                    # Guardar nueva foto
                    extension = foto.filename.rsplit('.', 1)[1].lower()
                    foto_filename = secure_filename(f"componente_{id}.{extension}")
                    filepath = os.path.join(current_app.config['UPLOAD_FOLDER_COMPONENTES'], foto_filename)
                    foto.save(filepath)
                else:
                    flash('Formato de imagen no válido. Use JPG, PNG o GIF.', 'error')
                    conn.close()
                    return render_template('componentes/editar.html', componente=componente)


            # Actualizar en la base de datos
            conn.execute('''
                UPDATE componentes SET 
                ID_Componente = ?, 
                Nombre = ?, 
                Tipo = ?, 
                Descripcion = ?, 
                Foto = ?, 
                Marca = ?, 
                Modelo = ?, 
                Precio = ?
                WHERE ID = ?
            ''', (codigo or None, nombre, tipo or None, descripcion or None, 
                  foto_filename, marca or None, modelo or None, precio_valor, id))
            
            conn.commit()
            flash('Componente actualizado correctamente.', 'success')
            print("=== ACTUALIZACIÓN EXITOSA ===")
            conn.close()
            return redirect(url_for('componentes.vista_componente', id=id))
            
        except sqlite3.Error as e:
            conn.rollback()
            flash(f'Error de base de datos: {str(e)}', 'error')
            print(f"Error SQL: {e}")
            conn.close()
            return render_template('componentes/editar.html', componente=componente)
        except Exception as e:
            conn.rollback()
            flash(f'Error inesperado: {str(e)}', 'error')
            print(f"Error general: {e}")
            conn.close()
            return render_template('componentes/editar.html', componente=componente)

    # GET: mostrar formulario
    conn.close()
    return render_template('componentes/editar.html', componente=componente)


# Component Deletion
@componentes_bp.route('/<int:id>/eliminar', methods=['POST'])
def eliminar_componente(id):
    conn = get_db_connection()
    componente = conn.execute('SELECT * FROM componentes WHERE ID = ?', (id,)).fetchone()
    
    if not componente:
        conn.close()
        flash('Componente no encontrado.', 'error')
        return redirect(url_for('componentes.lista_componentes'))


    
    try:
        # Eliminar foto si existe
        if componente['Foto']:
            foto_path = os.path.join(current_app.config['UPLOAD_FOLDER_COMPONENTES'], componente['Foto'])
            if os.path.exists(foto_path):
                try:
                    os.remove(foto_path)
                except OSError:
                    pass  # No importa si no se puede eliminar la foto
        
        # Eliminar relaciones en maquinas_componentes
        conn.execute('DELETE FROM maquinas_componentes WHERE ID_Componente = ?', (id,))
        
        # Eliminar frecuencias asociadas
        conn.execute('DELETE FROM frecuencias WHERE ID_Componente = ?', (id,))
        
        # Eliminar relaciones con proveedores
        conn.execute('DELETE FROM componentes_proveedores WHERE ID_Componente = ?', (id,))
        
        # Eliminar registros de stock
        conn.execute('DELETE FROM stock WHERE ID_Componente = ?', (componente['ID_Componente'],))
        
        # Eliminar compras (opcional - podrías querer mantener el historial)
        # conn.execute('DELETE FROM compras WHERE ID_Componente = ?', (id,))
        
        # Finalmente eliminar el componente
        cursor = conn.execute('DELETE FROM componentes WHERE ID = ?', (id,))
        
        if cursor.rowcount == 0:
            flash('No se pudo eliminar el componente.', 'error')
        else:
            flash(f'Componente "{componente["Nombre"]}" eliminado correctamente.', 'success')
        
        conn.commit()
    except sqlite3.Error as e:
        conn.rollback()
        flash(f'Error al eliminar el componente: {str(e)}', 'error')
    finally:
        conn.close()
    
    return redirect(url_for('componentes.lista_componentes'))



# Upload Component Photo
@componentes_bp.route('/<int:id>/upload_foto', methods=['POST'])
def upload_foto_componente(id):
    if 'foto' not in request.files:
        flash('No se encontró archivo en el formulario.')
        return redirect(url_for('componentes.vista_componente', id=id))

    foto = request.files['foto']
    if foto.filename == '':
        flash('Archivo vacío.')
        return redirect(url_for('componentes.vista_componente', id=id))


    if foto and allowed_file(foto.filename):
        extension = foto.filename.rsplit('.', 1)[1].lower()
        filename = secure_filename(f"componente_{id}.{extension}")
        filepath = os.path.join(current_app.config['UPLOAD_FOLDER_COMPONENTES'], filename)
        foto.save(filepath)

        # Actualizar en la base de datos
        conn = get_db_connection()
        conn.execute('UPDATE componentes SET Foto = ? WHERE ID = ?', (filename, id))
        conn.commit()
        conn.close()

        flash("Foto del componente actualizada.")
    else:
        flash("Formato de archivo no permitido.")

    return redirect(url_for('componentes.vista_componente', id=id))
