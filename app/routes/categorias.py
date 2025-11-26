from flask import Blueprint, request, jsonify
from app import db
from app.models import Categoria

categorias_bp = Blueprint('categorias', __name__)


@categorias_bp.route('', methods=['GET'])
def listar_categorias():
    """Lista todas as categorias"""
    apenas_ativas = request.args.get('ativas', 'true').lower() == 'true'
    
    query = Categoria.query
    if apenas_ativas:
        query = query.filter(Categoria.ativo == True)
    
    categorias = query.order_by(Categoria.nome).all()
    
    return jsonify({
        'success': True,
        'data': [cat.to_dict() for cat in categorias],
        'total': len(categorias)
    })


@categorias_bp.route('/<int:id>', methods=['GET'])
def obter_categoria(id):
    """Obtém uma categoria específica por ID"""
    categoria = Categoria.query.get_or_404(id)
    return jsonify({
        'success': True,
        'data': categoria.to_dict()
    })


@categorias_bp.route('', methods=['POST'])
def criar_categoria():
    """Cria uma nova categoria"""
    data = request.get_json()
    
    if not data:
        return jsonify({'success': False, 'error': 'Dados não fornecidos'}), 400
    
    if not data.get('nome'):
        return jsonify({'success': False, 'error': 'Nome é obrigatório'}), 400
    
    # Verifica se já existe categoria com esse nome
    if Categoria.query.filter_by(nome=data['nome']).first():
        return jsonify({'success': False, 'error': 'Já existe uma categoria com este nome'}), 400
    
    try:
        categoria = Categoria(
            nome=data['nome'],
            descricao=data.get('descricao'),
            cor=data.get('cor', '#007bff'),
            icone=data.get('icone', '📦'),
            ativo=data.get('ativo', True)
        )
        
        db.session.add(categoria)
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': 'Categoria criada com sucesso',
            'data': categoria.to_dict()
        }), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'error': str(e)}), 500


@categorias_bp.route('/<int:id>', methods=['PUT'])
def atualizar_categoria(id):
    """Atualiza uma categoria existente"""
    categoria = Categoria.query.get_or_404(id)
    data = request.get_json()
    
    if not data:
        return jsonify({'success': False, 'error': 'Dados não fornecidos'}), 400
    
    try:
        if 'nome' in data:
            # Verifica se já existe outra categoria com esse nome
            existing = Categoria.query.filter_by(nome=data['nome']).first()
            if existing and existing.id != id:
                return jsonify({'success': False, 'error': 'Já existe uma categoria com este nome'}), 400
            categoria.nome = data['nome']
        if 'descricao' in data:
            categoria.descricao = data['descricao']
        if 'cor' in data:
            categoria.cor = data['cor']
        if 'icone' in data:
            categoria.icone = data['icone']
        if 'ativo' in data:
            categoria.ativo = data['ativo']
        
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': 'Categoria atualizada com sucesso',
            'data': categoria.to_dict()
        })
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'error': str(e)}), 500


@categorias_bp.route('/<int:id>', methods=['DELETE'])
def deletar_categoria(id):
    """Deleta uma categoria (soft delete - apenas desativa)"""
    categoria = Categoria.query.get_or_404(id)
    
    try:
        # Soft delete - apenas desativa
        categoria.ativo = False
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': 'Categoria desativada com sucesso'
        })
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'error': str(e)}), 500


@categorias_bp.route('/seed', methods=['POST'])
def seed_categorias():
    """Popula categorias padrão"""
    categorias_padrao = [
        {'nome': 'Alimentação', 'descricao': 'Supermercado, restaurantes, lanches', 'cor': '#14b8a6', 'icone': '●'},
        {'nome': 'Transporte', 'descricao': 'Combustível, transporte público, apps', 'cor': '#0ea5e9', 'icone': '●'},
        {'nome': 'Moradia', 'descricao': 'Aluguel, condomínio, manutenção', 'cor': '#8b5cf6', 'icone': '●'},
        {'nome': 'Saúde', 'descricao': 'Médicos, remédios, plano de saúde', 'cor': '#10b981', 'icone': '●'},
        {'nome': 'Educação', 'descricao': 'Cursos, livros, material escolar', 'cor': '#f59e0b', 'icone': '●'},
        {'nome': 'Lazer', 'descricao': 'Cinema, viagens, entretenimento', 'cor': '#ec4899', 'icone': '●'},
        {'nome': 'Vestuário', 'descricao': 'Roupas, calçados, acessórios', 'cor': '#f43f5e', 'icone': '●'},
        {'nome': 'Contas Fixas', 'descricao': 'Água, luz, internet, telefone', 'cor': '#64748b', 'icone': '●'},
        {'nome': 'Salário', 'descricao': 'Rendimentos mensais', 'cor': '#22c55e', 'icone': '●'},
        {'nome': 'Investimentos', 'descricao': 'Rendimentos de investimentos', 'cor': '#eab308', 'icone': '●'},
        {'nome': 'Outros', 'descricao': 'Gastos diversos', 'cor': '#6b7280', 'icone': '●'},
    ]
    
    criadas = 0
    for cat_data in categorias_padrao:
        if not Categoria.query.filter_by(nome=cat_data['nome']).first():
            categoria = Categoria(**cat_data)
            db.session.add(categoria)
            criadas += 1
    
    db.session.commit()
    
    return jsonify({
        'success': True,
        'message': f'{criadas} categorias criadas com sucesso'
    })
