from flask import Blueprint, request, jsonify
from app import db
from app.models import Gasto, Categoria
from datetime import datetime

gastos_bp = Blueprint('gastos', __name__)


@gastos_bp.route('', methods=['GET'])
def listar_gastos():
    """Lista todos os gastos com filtros opcionais"""
    # Parâmetros de filtro
    categoria_id = request.args.get('categoria_id', type=int)
    tipo = request.args.get('tipo')
    data_inicio = request.args.get('data_inicio')
    data_fim = request.args.get('data_fim')
    mes = request.args.get('mes', type=int)
    ano = request.args.get('ano', type=int)
    
    # Query base
    query = Gasto.query
    
    # Aplica filtros
    if categoria_id:
        query = query.filter(Gasto.categoria_id == categoria_id)
    if tipo:
        query = query.filter(Gasto.tipo == tipo)
    if data_inicio:
        query = query.filter(Gasto.data >= datetime.strptime(data_inicio, '%Y-%m-%d').date())
    if data_fim:
        query = query.filter(Gasto.data <= datetime.strptime(data_fim, '%Y-%m-%d').date())
    if mes and ano:
        query = query.filter(
            db.extract('month', Gasto.data) == mes,
            db.extract('year', Gasto.data) == ano
        )
    
    # Ordenação por data (mais recente primeiro)
    gastos = query.order_by(Gasto.data.desc()).all()
    
    return jsonify({
        'success': True,
        'data': [gasto.to_dict() for gasto in gastos],
        'total': len(gastos)
    })


@gastos_bp.route('/<int:id>', methods=['GET'])
def obter_gasto(id):
    """Obtém um gasto específico por ID"""
    gasto = Gasto.query.get_or_404(id)
    return jsonify({
        'success': True,
        'data': gasto.to_dict()
    })


@gastos_bp.route('', methods=['POST'])
def criar_gasto():
    """Cria um novo gasto"""
    data = request.get_json()
    
    if not data:
        return jsonify({'success': False, 'error': 'Dados não fornecidos'}), 400
    
    # Validações básicas
    if not data.get('descricao'):
        return jsonify({'success': False, 'error': 'Descrição é obrigatória'}), 400
    if not data.get('valor'):
        return jsonify({'success': False, 'error': 'Valor é obrigatório'}), 400
    
    try:
        gasto = Gasto(
            descricao=data['descricao'],
            valor=data['valor'],
            data=datetime.strptime(data.get('data', datetime.now().strftime('%Y-%m-%d')), '%Y-%m-%d').date(),
            categoria_id=data.get('categoria_id'),
            tipo=data.get('tipo', 'despesa'),
            forma_pagamento=data.get('forma_pagamento'),
            observacao=data.get('observacao'),
            recorrente=data.get('recorrente', False)
        )
        
        db.session.add(gasto)
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': 'Gasto criado com sucesso',
            'data': gasto.to_dict()
        }), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'error': str(e)}), 500


@gastos_bp.route('/<int:id>', methods=['PUT'])
def atualizar_gasto(id):
    """Atualiza um gasto existente"""
    gasto = Gasto.query.get_or_404(id)
    data = request.get_json()
    
    if not data:
        return jsonify({'success': False, 'error': 'Dados não fornecidos'}), 400
    
    try:
        if 'descricao' in data:
            gasto.descricao = data['descricao']
        if 'valor' in data:
            gasto.valor = data['valor']
        if 'data' in data:
            gasto.data = datetime.strptime(data['data'], '%Y-%m-%d').date()
        if 'categoria_id' in data:
            gasto.categoria_id = data['categoria_id']
        if 'tipo' in data:
            gasto.tipo = data['tipo']
        if 'forma_pagamento' in data:
            gasto.forma_pagamento = data['forma_pagamento']
        if 'observacao' in data:
            gasto.observacao = data['observacao']
        if 'recorrente' in data:
            gasto.recorrente = data['recorrente']
        
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': 'Gasto atualizado com sucesso',
            'data': gasto.to_dict()
        })
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'error': str(e)}), 500


@gastos_bp.route('/<int:id>', methods=['DELETE'])
def deletar_gasto(id):
    """Deleta um gasto"""
    gasto = Gasto.query.get_or_404(id)
    
    try:
        db.session.delete(gasto)
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': 'Gasto deletado com sucesso'
        })
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'error': str(e)}), 500
