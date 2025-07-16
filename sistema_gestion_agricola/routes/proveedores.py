# routes/proveedores.py
from flask import Blueprint, render_template, request, redirect, url_for, flash
from ..models import db, Proveedor, Componente, ComponentesProveedores

proveedores_bp = Blueprint('proveedores', __name__, url_prefix='/proveedor')

# List Providers
@proveedores_bp.route('/')
def listar_proveedores():
    proveedores = Proveedor.query.all()
    return render_template('proveedores/listar.html', proveedores=proveedores)

# Create Provider
@proveedores_bp.route('/agregar', methods=['GET', 'POST'])
def agregar_proveedor():
    if request.method == 'POST':
        nombre = request.form['nombre'].strip()
        if not nombre:
            flash('El nombre es obligatorio.')
            return redirect(url_for('proveedores.agregar_proveedor'))
        
        proveedor = Proveedor(
            Nombre=nombre,
            Localidad=request.form.get('localidad', ''),
            Contacto=request.form.get('contacto', ''),
            Telefono=request.form.get('telefono', ''),
            Email=request.form.get('email', ''),
            Rubro=request.form.get('rubro', ''),
            Direccion=request.form.get('direccion', ''),
            Observaciones=request.form.get('observaciones', '')
        )
        db.session.add(proveedor)
        db.session.commit()
        flash(f'Proveedor "{nombre}" agregado correctamente.')
        return redirect(url_for('proveedores.listar_proveedores'))

    return render_template('proveedores/agregar.html')

# Read Provider
@proveedores_bp.route('/<int:id>')
def ver_proveedor(id):
    proveedor = Proveedor.query.get_or_404(id)
    componentes_asociados = proveedor.componentes   # lista de ComponentesProveedores con cantidad

    return render_template('proveedores/ver.html', proveedor=proveedor, componentes_asociados=componentes_asociados)

# Update Provider
@proveedores_bp.route('/<int:id>/editar', methods=['GET', 'POST'])
def editar_proveedor(id):
    proveedor = Proveedor.query.get_or_404(id)

    if request.method == 'POST':
        nombre = request.form['nombre'].strip()
        if not nombre:
            flash('El nombre es obligatorio.')
            return redirect(url_for('proveedores.editar_proveedor', id=id))

        proveedor.Nombre = nombre
        proveedor.Localidad = request.form.get('localidad', '')
        proveedor.Contacto = request.form.get('contacto', '')
        proveedor.Telefono = request.form.get('telefono', '')
        proveedor.Email = request.form.get('email', '')
        proveedor.Rubro = request.form.get('rubro', '')
        proveedor.Direccion = request.form.get('direccion', '')
        proveedor.Observaciones = request.form.get('observaciones', '')

        db.session.commit()
        flash(f'Proveedor "{nombre}" actualizado correctamente.')
        return redirect(url_for('proveedores.listar_proveedores'))

    return render_template('proveedores/editar.html', proveedor=proveedor)

# Delete Provider
@proveedores_bp.route('/<int:id>/eliminar', methods=['POST'])
def eliminar_proveedor(id):
    proveedor = Proveedor.query.get_or_404(id)
    nombre = proveedor.Nombre
    db.session.delete(proveedor)
    db.session.commit()
    flash(f'Proveedor "{nombre}" eliminado correctamente.')
    return redirect(url_for('proveedores.listar_proveedores'))

# Assign Components to Provider
@proveedores_bp.route('/<int:id_proveedor>/componentes/asignar', methods=['GET', 'POST'])
def asignar_componente_proveedor(id_proveedor):
    proveedor = Proveedor.query.get_or_404(id_proveedor)

    if request.method == 'POST':
        componentes_ids = request.form.getlist('componentes[]')
        if not componentes_ids:
            flash("Seleccioná al menos un componente.")
            return redirect(url_for('proveedores.asignar_componente_proveedor', id_proveedor=id_proveedor))

        for id_comp in componentes_ids:
            componente = Componente.query.get(id_comp)
            if not componente:
                flash(f"Componente {id_comp} no válido.")
                continue
            # Verificar si ya existe la asociación
            assoc = ComponentesProveedores.query.filter_by(ID_Proveedor=id_proveedor, ID_Componente=id_comp).first()
            if not assoc:
                assoc = ComponentesProveedores(ID_Proveedor=id_proveedor, ID_Componente=id_comp, Cantidad=1)
                db.session.add(assoc)

        db.session.commit()
        flash("Componentes asignados correctamente.")
        return redirect(url_for('proveedores.ver_proveedor', id=id_proveedor))

    # Componentes no asignados aún a este proveedor
    componentes_asignados_ids = [cp.ID_Componente for cp in proveedor.componentes ]
    componentes_disponibles = Componente.query.filter(~Componente.ID.in_(componentes_asignados_ids)).all()

    return render_template('proveedores/asignar_componente.html',
                           proveedor=proveedor,
                           componentes_disponibles=componentes_disponibles)

# Edit Provider-Component Association (e.g. Cantidad)
@proveedores_bp.route('/<int:id_proveedor>/componentes/<int:id_componente>/editar', methods=['GET', 'POST'])
def editar_componente_proveedor(id_proveedor, id_componente):
    assoc = ComponentesProveedores.query.filter_by(ID_Proveedor=id_proveedor, ID_Componente=id_componente).first_or_404()
    
    componentes = Componente.query.all() 

    if request.method == 'POST':
        try:
            nuevo_componente = int(request.form.get('componente'))
            cantidad = int(request.form.get('cantidad', 1))

            if cantidad < 1:
                raise ValueError
            
            ya_existe = ComponentesProveedores.query.filter_by(
                ID_Proveedor=id_proveedor,
                ID_Componente=nuevo_componente
            ).first()

            if ya_existe:
                # Si es la misma que estamos editando, solo actualizamos cantidad
                if ya_existe.ID_Proveedor == assoc.ID_Proveedor and ya_existe.ID_Componente == assoc.ID_Componente:
                    assoc.Cantidad = cantidad
                else:
                    # Sumar la cantidad a la existente y eliminar la actual
                    ya_existe.Cantidad += cantidad
                    db.session.delete(assoc)
            else:
                # Si no existe, simplemente actualizamos el objeto actual
                assoc.ID_Componente = nuevo_componente
                assoc.Cantidad = cantidad

            db.session.commit()
            flash("Componente asociado actualizado.")
            return redirect(url_for('proveedores.ver_proveedor', id=id_proveedor))
        except (ValueError, TypeError):
            flash("Datos inválidos.")
            return redirect(request.url)

    return render_template('proveedores/editar_componente_proveedor.html',
                           proveedor=assoc.proveedor,
                           componente=assoc.componente,
                           componentes=componentes,
                           cantidad=assoc.Cantidad)

# Delete Provider-Component Association
@proveedores_bp.route('/<int:id_proveedor>/componentes/<int:id_componente>/eliminar', methods=['POST'])
def eliminar_componente_proveedor(id_proveedor, id_componente):
    assoc = ComponentesProveedores.query.filter_by(ID_Proveedor=id_proveedor, ID_Componente=id_componente).first()
    if not assoc:
        flash("Asociación no encontrada.")
        return redirect(url_for('proveedores.ver_proveedor', id=id_proveedor))

    db.session.delete(assoc)
    db.session.commit()
    flash("Componente asociado eliminado correctamente.")
    return redirect(url_for('proveedores.ver_proveedor', id=id_proveedor))
