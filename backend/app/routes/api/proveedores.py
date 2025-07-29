from flask import request, jsonify
from werkzeug.exceptions import BadRequest
from . import api_bp
from ...models import Proveedor
from ...utils.db import db, commit_or_rollback

@api_bp.route('/proveedores', methods=['GET'])
def get_proveedores():
    try:
        activo = request.args.get('activo', 'true').lower() == 'true'
        search = request.args.get('search', '').strip()
        
        query = Proveedor.query.filter(Proveedor.activo == activo)
        
        if search:
            query = query.filter(
                db.or_(
                    Proveedor.nombre.ilike(f'%{search}%'),
                    Proveedor.razon_social.ilike(f'%{search}%'),
                    Proveedor.cuit.ilike(f'%{search}%')
                )
            )
        
        proveedores = query.order_by(Proveedor.nombre).all()
        
        return jsonify({
            'success': True,
            'data': [prov.to_dict() for prov in proveedores],
            'total': len(proveedores)
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@api_bp.route('/proveedores', methods=['POST'])
def create_proveedor():
    try:
        data = request.get_json()
        
        if not data.get('nombre'):
            raise BadRequest("El nombre es requerido")
        
        # Verificar CUIT único
        if data.get('cuit'):
            existing = Proveedor.query.filter_by(cuit=data['cuit']).first()
            if existing:
                raise BadRequest("El CUIT ya existe")
        
        proveedor = Proveedor(
            nombre=data.get('nombre'),
            razon_social=data.get('razon_social'),
            cuit=data.get('cuit'),
            telefono=data.get('telefono'),
            email=data.get('email'),
            direccion=data.get('direccion'),
            ciudad=data.get('ciudad'),
            provincia=data.get('provincia'),
            codigo_postal=data.get('codigo_postal'),
            contacto=data.get('contacto'),
            condicion_iva=data.get('condicion_iva'),
            forma_pago=data.get('forma_pago')
        )
        
        db.session.add(proveedor)
        commit_or_rollback()
        
        return jsonify({
            'success': True,
            'data': proveedor.to_dict(),
            'message': 'Proveedor creado exitosamente'
        }), 201
        
    except BadRequest as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 400
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@api_bp.route('/proveedores/<int:id>', methods=['GET'])
def get_proveedor(id):
    try:
        proveedor = Proveedor.query.get_or_404(id)
        include_relations = request.args.get('include_relations', 'false').lower() == 'true'
        
        return jsonify({
            'success': True,
            'data': proveedor.to_dict(include_relations=include_relations)
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@api_bp.route('/proveedores/<int:id>', methods=['PUT'])
def update_proveedor(id):
    try:
        proveedor = Proveedor.query.get_or_404(id)
        data = request.get_json()
        
        # Verificar CUIT único
        if data.get('cuit') and data['cuit'] != proveedor.cuit:
            existing = Proveedor.query.filter_by(cuit=data['cuit']).first()
            if existing:
                raise BadRequest("El CUIT ya existe")
        
        # Actualizar campos
        fields = ['nombre', 'razon_social', 'cuit', 'telefono', 'email', 'direccion', 
                 'ciudad', 'provincia', 'codigo_postal', 'contacto', 'condicion_iva', 
                 'forma_pago', 'activo']
        
        for field in fields:
            if field in data:
                setattr(proveedor, field, data[field])
        
        commit_or_rollback()
        
        return jsonify({
            'success': True,
            'data': proveedor.to_dict(),
            'message': 'Proveedor actualizado exitosamente'
        })
        
    except BadRequest as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 400
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500