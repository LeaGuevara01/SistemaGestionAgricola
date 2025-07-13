# routes/proveedores.py
from flask import Blueprint, render_template, request, redirect, url_for, flash
from ..utils.db import get_db_connection

proveedores_bp = Blueprint('proveedores', __name__, url_prefix='/proveedor')

# List Providers
@proveedores_bp.route('/')
def listar_proveedores():
    conn = get_db_connection()
    proveedores = conn.execute('SELECT * FROM proveedores').fetchall()
    conn.close()
    return render_template('proveedores/listar.html', proveedores=proveedores)

# Create Provider
@proveedores_bp.route('/agregar', methods=['GET', 'POST'])
def agregar_proveedor():
    if request.method == 'POST':
        nombre = request.form['nombre']
        localidad = request.form.get('localidad', '')
        contacto = request.form.get('contacto', '')
        telefono = request.form.get('telefono', '')
        email = request.form.get('email', '')
        rubro = request.form.get('rubro', '')
        direccion = request.form.get('direccion', '')
        observaciones = request.form.get('observaciones', '')

        if not nombre.strip():
            flash('El nombre es obligatorio.')
            return redirect(url_for('proveedores.agregar_proveedor'))

        conn = get_db_connection()
        conn.execute('''
            INSERT INTO proveedores (Nombre, Localidad, Contacto, Telefono, Email, Rubro, Direccion, Observaciones)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        ''', (nombre, localidad, contacto, telefono, email, rubro, direccion, observaciones))
        conn.commit()
        conn.close()

        flash(f'Proveedor "{nombre}" agregado correctamente.')
        return redirect(url_for('proveedores.listar_proveedores'))

    return render_template('proveedores/agregar.html')

# Read Provider
@proveedores_bp.route('/<int:id>')
def ver_proveedor(id):
    conn = get_db_connection()

    # Obtener proveedor
    proveedor = conn.execute('SELECT * FROM proveedores WHERE ID = ?', (id,)).fetchone()
    if not proveedor:
        conn.close()
        flash('Proveedor no encontrado.')
        return redirect(url_for('proveedores.listar_proveedores'))

    # Obtener componentes asociados
    componentes_asociados = conn.execute('''
        SELECT c.ID, c.Nombre, c.Descripcion, cp.Cantidad
        FROM componentes c
        JOIN componentes_proveedores cp ON c.ID = cp.ID_Componente
        WHERE cp.ID_Proveedor = ?
    ''', (id,)).fetchall()

    conn.close()

    return render_template('proveedores/ver.html', proveedor=proveedor, componentes_asociados=componentes_asociados)

# Update Provider
@proveedores_bp.route('/<int:id>/editar', methods=['GET', 'POST'])
def editar_proveedor(id):
    conn = get_db_connection()
    proveedor = conn.execute('SELECT * FROM proveedores WHERE ID = ?', (id,)).fetchone()
    if proveedor is None:
        conn.close()
        flash('Proveedor no encontrado.')
        return redirect(url_for('proveedores.listar_proveedores'))

    if request.method == 'POST':
        nombre = request.form['nombre']
        localidad = request.form.get('localidad', '')
        contacto = request.form.get('contacto', '')
        telefono = request.form.get('telefono', '')
        email = request.form.get('email', '')
        rubro = request.form.get('rubro', '')
        direccion = request.form.get('direccion', '')
        observaciones = request.form.get('observaciones', '')

        if not nombre.strip():
            flash('El nombre es obligatorio.')
            conn.close()
            return redirect(url_for('proveedores.editar_proveedor', id=id))

        conn.execute('''
            UPDATE proveedores SET
            Nombre = ?, Localidad = ?, Contacto = ?, Telefono = ?, Email = ?, Rubro = ?, Direccion = ?, Observaciones = ?
            WHERE ID = ?
        ''', (nombre, localidad, contacto, telefono, email, rubro, direccion, observaciones, id))
        conn.commit()
        conn.close()

        flash(f'Proveedor "{nombre}" actualizado correctamente.')
        return redirect(url_for('proveedores.listar_proveedores'))

    conn.close()
    return render_template('proveedores/editar.html', proveedor=proveedor)

# Delete Provider
@proveedores_bp.route('/<int:id>/eliminar', methods=['POST'])
def eliminar_proveedor(id):
    conn = get_db_connection()
    proveedor = conn.execute('SELECT * FROM proveedores WHERE ID = ?', (id,)).fetchone()
    if proveedor is None:
        conn.close()
        flash('Proveedor no encontrado.')
        return redirect(url_for('proveedores.listar_proveedores'))

    conn.execute('DELETE FROM proveedores WHERE ID = ?', (id,))
    conn.commit()
    conn.close()

    flash(f'Proveedor "{proveedor["Nombre"]}" eliminado correctamente.')
    return redirect(url_for('proveedores.listar_proveedores'))


# Create Provider-Component Reference
@proveedores_bp.route('/<int:id_proveedor>/componentes/asignar', methods=['GET', 'POST'])
def asignar_componente_proveedor(id_proveedor):
    conn = get_db_connection()

    proveedor = conn.execute('SELECT * FROM proveedores WHERE ID = ?', (id_proveedor,)).fetchone()
    if not proveedor:
        flash("Proveedor no encontrado.")
        conn.close()
        return redirect(url_for('proveedores.listar_proveedores'))

    if request.method == 'POST':
        componentes_ids = request.form.getlist('componentes[]')  # lista de componentes seleccionados
        if not componentes_ids:
            flash("Seleccioná al menos un componente.")
            conn.close()
            return redirect(url_for('proveedores.asignar_componente_proveedor', id_proveedor=id_proveedor))

        for id_comp in componentes_ids:
            componente = conn.execute('SELECT * FROM componentes WHERE ID = ?', (id_comp,)).fetchone()
            if not componente:
                flash(f"Componente {id_comp} no válido.")
                continue

            conn.execute('''
                INSERT OR IGNORE INTO componentes_proveedores (ID_Proveedor, ID_Componente)
                VALUES (?, ?)
            ''', (id_proveedor, id_comp))

        conn.commit()
        conn.close()
        flash("Componentes asignados correctamente.")
        return redirect(url_for('proveedores.ver_proveedor', id=id_proveedor))

    # Si es GET, mostramos el formulario con componentes disponibles
    componentes_disponibles = conn.execute('''
        SELECT * FROM componentes
        WHERE ID NOT IN (
            SELECT ID_Componente FROM componentes_proveedores WHERE ID_Proveedor = ?
        )
    ''', (id_proveedor,)).fetchall()
    conn.close()

    return render_template('proveedores/asignar_componente.html',
                           proveedor=proveedor,
                           componentes_disponibles=componentes_disponibles)


# Update Provider-Component Reference
@proveedores_bp.route('/<int:id_proveedor>/componentes/<int:id_componente>/editar', methods=['GET', 'POST'])
def editar_componente_proveedor(id_proveedor, id_componente):
    conn = get_db_connection()

    # Obtener asociación actual
    assoc = conn.execute('''
        SELECT * FROM componentes_proveedores
        WHERE ID_Proveedor = ? AND ID_Componente = ?
    ''', (id_proveedor, id_componente)).fetchone()

    if not assoc:
        flash("Asociación no encontrada.")
        conn.close()
        return redirect(url_for('proveedores.ver_proveedor', id=id_proveedor))

    if request.method == 'POST':
        cantidad = request.form.get('cantidad', 1)

        conn.execute('''
            UPDATE componentes_proveedores
            SET cantidad = ?
            WHERE ID_Proveedor = ? AND ID_Componente = ?
        ''', (cantidad, id_proveedor, id_componente))
        conn.commit()
        conn.close()

        flash("Componente asociado actualizado.")
        return redirect(url_for('proveedores.ver_proveedor', id=id_proveedor))

    # Obtener datos para mostrar en el formulario
    componente = conn.execute('SELECT * FROM componentes WHERE ID = ?', (id_componente,)).fetchone()
    proveedor = conn.execute('SELECT * FROM proveedores WHERE ID = ?', (id_proveedor,)).fetchone()
    conn.close()

    return render_template('proveedores/editar_componente_proveedor.html',
                           proveedor=proveedor,
                           componente=componente,
                           cantidad=assoc['cantidad'])


# Delete Provider-Component Reference
@proveedores_bp.route('/<int:id_proveedor>/componentes/<int:id_componente>/eliminar', methods=['POST'])
def eliminar_componente_proveedor(id_proveedor, id_componente):
    conn = get_db_connection()

    assoc = conn.execute('''
        SELECT * FROM componentes_proveedores
        WHERE ID_Proveedor = ? AND ID_Componente = ?
    ''', (id_proveedor, id_componente)).fetchone()

    if not assoc:
        flash("Asociación no encontrada.")
        conn.close()
        return redirect(url_for('proveedores.ver_proveedor', id=id_proveedor))

    conn.execute('''
        DELETE FROM componentes_proveedores
        WHERE ID_Proveedor = ? AND ID_Componente = ?
    ''', (id_proveedor, id_componente))
    conn.commit()
    conn.close()

    flash("Componente asociado eliminado correctamente.")
    return redirect(url_for('proveedores.ver_proveedor', id=id_proveedor))
