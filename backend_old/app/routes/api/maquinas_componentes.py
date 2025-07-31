from flask import request, jsonify
from werkzeug.exceptions import BadRequest
from . import api_bp
from ...models.maquina import Maquina
from ...models.componente import Componente
from ...models.asociaciones import maquinas_componentes
from ...utils.db import db, commit_or_rollback

@api_bp.route('/maquinas/<int:maquina_id>/componentes', methods=['GET'])
def get_maquina_componentes(maquina_id):
    """Obtener componentes asociados a una máquina"""
    try:
        maquina = Maquina.query.get_or_404(maquina_id)
        
        # Obtener componentes usando la tabla de asociación
        query = db.session.query(Componente).join(
            maquinas_componentes,
            Componente.id == maquinas_componentes.c.ID_Componente
        ).filter(
            maquinas_componentes.c.ID_Maquina == maquina_id
        )
        
        search = request.args.get('search', '').strip()
        if search:
            query = query.filter(
                db.or_(
                    Componente.nombre.ilike(f'%{search}%'),
                    getattr(Componente, 'Descripcion', '').ilike(f'%{search}%')
                )
            )
        
        componentes = query.order_by(Componente.nombre).all()
        
        return jsonify({
            'success': True,
            'data': [comp.to_dict() for comp in componentes],
            'total': len(componentes),
            'maquina': maquina.to_dict()
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@api_bp.route('/maquinas/<int:maquina_id>/componentes/<int:componente_id>', methods=['POST'])
def asignar_componente_maquina(maquina_id, componente_id):
    """Asignar un componente a una máquina"""
    try:
        maquina = Maquina.query.get_or_404(maquina_id)
        componente = Componente.query.get_or_404(componente_id)
        
        # Verificar si la asociación ya existe
        existing = db.session.query(maquinas_componentes).filter(
            maquinas_componentes.c.ID_Maquina == maquina_id,
            maquinas_componentes.c.ID_Componente == componente_id
        ).first()
        
        if existing:
            return jsonify({
                'success': False,
                'error': 'El componente ya está asignado a esta máquina'
            }), 400
        
        # Crear la asociación
        insert_stmt = maquinas_componentes.insert().values(
            ID_Maquina=maquina_id,
            ID_Componente=componente_id
        )
        db.session.execute(insert_stmt)
        commit_or_rollback()
        
        return jsonify({
            'success': True,
            'message': f'Componente "{componente.nombre}" asignado a la máquina "{maquina.nombre}"'
        })
        
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@api_bp.route('/maquinas/<int:maquina_id>/componentes/<int:componente_id>', methods=['DELETE'])
def desasignar_componente_maquina(maquina_id, componente_id):
    """Desasignar un componente de una máquina"""
    try:
        # Verificar que la asociación existe
        existing = db.session.query(maquinas_componentes).filter(
            maquinas_componentes.c.ID_Maquina == maquina_id,
            maquinas_componentes.c.ID_Componente == componente_id
        ).first()
        
        if not existing:
            return jsonify({
                'success': False,
                'error': 'El componente no está asignado a esta máquina'
            }), 404
        
        # Eliminar la asociación
        delete_stmt = maquinas_componentes.delete().where(
            db.and_(
                maquinas_componentes.c.ID_Maquina == maquina_id,
                maquinas_componentes.c.ID_Componente == componente_id
            )
        )
        db.session.execute(delete_stmt)
        commit_or_rollback()
        
        return jsonify({
            'success': True,
            'message': 'Componente desasignado de la máquina correctamente'
        })
        
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@api_bp.route('/maquinas/<int:maquina_id>/componentes/disponibles', methods=['GET'])
def get_componentes_disponibles(maquina_id):
    """Obtener componentes disponibles para asignar a una máquina"""
    try:
        maquina = Maquina.query.get_or_404(maquina_id)
        
        # Obtener componentes que NO están asignados a esta máquina
        subquery = db.session.query(maquinas_componentes.c.ID_Componente).filter(
            maquinas_componentes.c.ID_Maquina == maquina_id
        )
        
        query = Componente.query.filter(
            ~Componente.id.in_(subquery.scalar_subquery())
        )
        
        search = request.args.get('search', '').strip()
        if search:
            query = query.filter(
                db.or_(
                    Componente.nombre.ilike(f'%{search}%'),
                    getattr(Componente, 'Descripcion', '').ilike(f'%{search}%')
                )
            )
        
        categoria = request.args.get('categoria')
        if categoria and categoria.strip():
            query = query.filter(getattr(Componente, 'Tipo') == categoria)
        
        componentes = query.order_by(Componente.nombre).limit(100).all()
        
        return jsonify({
            'success': True,
            'data': [comp.to_dict() for comp in componentes],
            'total': len(componentes),
            'maquina': maquina.to_dict()
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@api_bp.route('/componentes/<int:componente_id>/maquinas', methods=['GET'])
def get_componente_maquinas(componente_id):
    """Obtener máquinas que usan un componente específico"""
    try:
        componente = Componente.query.get_or_404(componente_id)
        
        # Obtener máquinas usando la tabla de asociación
        query = db.session.query(Maquina).join(
            maquinas_componentes,
            Maquina.id == maquinas_componentes.c.ID_Maquina
        ).filter(
            maquinas_componentes.c.ID_Componente == componente_id
        )
        
        search = request.args.get('search', '').strip()
        if search:
            query = query.filter(
                db.or_(
                    Maquina.nombre.ilike(f'%{search}%'),
                    getattr(Maquina, 'Marca', '').ilike(f'%{search}%')
                )
            )
        
        maquinas = query.order_by(Maquina.nombre).all()
        
        return jsonify({
            'success': True,
            'data': [maq.to_dict() for maq in maquinas],
            'total': len(maquinas),
            'componente': componente.to_dict()
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@api_bp.route('/maquinas/<int:maquina_id>/componentes/masivo', methods=['POST'])
def asignar_componentes_masivo(maquina_id):
    """Asignar múltiples componentes a una máquina"""
    try:
        maquina = Maquina.query.get_or_404(maquina_id)
        data = request.get_json()
        
        if not data or 'componentes_ids' not in data:
            raise BadRequest("Se requiere la lista de componentes_ids")
        
        componentes_ids = data['componentes_ids']
        if not isinstance(componentes_ids, list):
            raise BadRequest("componentes_ids debe ser una lista")
        
        asignados = 0
        errores = []
        
        for componente_id in componentes_ids:
            try:
                # Verificar que el componente existe
                componente = Componente.query.get(componente_id)
                if not componente:
                    errores.append(f"Componente ID {componente_id} no encontrado")
                    continue
                
                # Verificar si ya está asignado
                existing = db.session.query(maquinas_componentes).filter(
                    maquinas_componentes.c.ID_Maquina == maquina_id,
                    maquinas_componentes.c.ID_Componente == componente_id
                ).first()
                
                if existing:
                    errores.append(f"Componente '{componente.nombre}' ya está asignado")
                    continue
                
                # Crear la asociación
                insert_stmt = maquinas_componentes.insert().values(
                    ID_Maquina=maquina_id,
                    ID_Componente=componente_id
                )
                db.session.execute(insert_stmt)
                asignados += 1
                
            except Exception as e:
                errores.append(f"Error con componente ID {componente_id}: {str(e)}")
        
        commit_or_rollback()
        
        return jsonify({
            'success': True,
            'message': f'Se asignaron {asignados} componentes a la máquina "{maquina.nombre}"',
            'asignados': asignados,
            'errores': errores
        })
        
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500
