from flask import Blueprint, request, jsonify
from app import db
from app.models import Gasto, Categoria
from datetime import datetime, timedelta
from sqlalchemy import func, extract

relatorios_bp = Blueprint('relatorios', __name__)


@relatorios_bp.route('/resumo-mensal', methods=['GET'])
def resumo_mensal():
    """Retorna resumo de gastos do mês"""
    mes = request.args.get('mes', datetime.now().month, type=int)
    ano = request.args.get('ano', datetime.now().year, type=int)
    
    # Total de despesas
    total_despesas = db.session.query(func.sum(Gasto.valor)).filter(
        Gasto.tipo == 'despesa',
        extract('month', Gasto.data) == mes,
        extract('year', Gasto.data) == ano
    ).scalar() or 0
    
    # Total de receitas
    total_receitas = db.session.query(func.sum(Gasto.valor)).filter(
        Gasto.tipo == 'receita',
        extract('month', Gasto.data) == mes,
        extract('year', Gasto.data) == ano
    ).scalar() or 0
    
    # Saldo
    saldo = float(total_receitas) - float(total_despesas)
    
    # Quantidade de transações
    qtd_transacoes = Gasto.query.filter(
        extract('month', Gasto.data) == mes,
        extract('year', Gasto.data) == ano
    ).count()
    
    return jsonify({
        'success': True,
        'data': {
            'mes': mes,
            'ano': ano,
            'total_despesas': float(total_despesas),
            'total_receitas': float(total_receitas),
            'saldo': saldo,
            'quantidade_transacoes': qtd_transacoes
        }
    })


@relatorios_bp.route('/por-categoria', methods=['GET'])
def gastos_por_categoria():
    """Retorna gastos agrupados por categoria"""
    mes = request.args.get('mes', datetime.now().month, type=int)
    ano = request.args.get('ano', datetime.now().year, type=int)
    tipo = request.args.get('tipo', 'despesa')
    
    # Query com agrupamento por categoria
    resultados = db.session.query(
        Categoria.id,
        Categoria.nome,
        Categoria.cor,
        Categoria.icone,
        func.sum(Gasto.valor).label('total'),
        func.count(Gasto.id).label('quantidade')
    ).join(Gasto, Categoria.id == Gasto.categoria_id)\
    .filter(
        Gasto.tipo == tipo,
        extract('month', Gasto.data) == mes,
        extract('year', Gasto.data) == ano
    ).group_by(Categoria.id).all()
    
    # Calcula total geral para porcentagem
    total_geral = sum(r.total for r in resultados) if resultados else 0
    
    dados = []
    for r in resultados:
        dados.append({
            'categoria_id': r.id,
            'categoria_nome': r.nome,
            'cor': r.cor,
            'icone': r.icone,
            'total': float(r.total),
            'quantidade': r.quantidade,
            'percentual': round((float(r.total) / float(total_geral)) * 100, 2) if total_geral > 0 else 0
        })
    
    # Ordena por total (maior primeiro)
    dados.sort(key=lambda x: x['total'], reverse=True)
    
    return jsonify({
        'success': True,
        'data': {
            'mes': mes,
            'ano': ano,
            'tipo': tipo,
            'total_geral': float(total_geral),
            'categorias': dados
        }
    })


@relatorios_bp.route('/evolucao', methods=['GET'])
def evolucao_gastos():
    """Retorna evolução de gastos nos últimos meses"""
    meses = request.args.get('meses', 6, type=int)
    tipo = request.args.get('tipo')  # Se não informado, retorna ambos
    
    hoje = datetime.now()
    dados = []
    
    for i in range(meses - 1, -1, -1):
        # Calcula o mês
        data_ref = hoje - timedelta(days=i * 30)
        mes = data_ref.month
        ano = data_ref.year
        
        # Query para despesas
        despesas = db.session.query(func.sum(Gasto.valor)).filter(
            Gasto.tipo == 'despesa',
            extract('month', Gasto.data) == mes,
            extract('year', Gasto.data) == ano
        ).scalar() or 0
        
        # Query para receitas
        receitas = db.session.query(func.sum(Gasto.valor)).filter(
            Gasto.tipo == 'receita',
            extract('month', Gasto.data) == mes,
            extract('year', Gasto.data) == ano
        ).scalar() or 0
        
        item = {
            'mes': mes,
            'ano': ano,
            'mes_nome': data_ref.strftime('%b/%Y')
        }
        
        if tipo == 'despesa':
            item['valor'] = float(despesas)
        elif tipo == 'receita':
            item['valor'] = float(receitas)
        else:
            item['despesas'] = float(despesas)
            item['receitas'] = float(receitas)
            item['saldo'] = float(receitas) - float(despesas)
        
        dados.append(item)
    
    return jsonify({
        'success': True,
        'data': dados
    })


@relatorios_bp.route('/maiores-gastos', methods=['GET'])
def maiores_gastos():
    """Retorna os maiores gastos do período"""
    mes = request.args.get('mes', datetime.now().month, type=int)
    ano = request.args.get('ano', datetime.now().year, type=int)
    limite = request.args.get('limite', 10, type=int)
    
    gastos = Gasto.query.filter(
        Gasto.tipo == 'despesa',
        extract('month', Gasto.data) == mes,
        extract('year', Gasto.data) == ano
    ).order_by(Gasto.valor.desc()).limit(limite).all()
    
    return jsonify({
        'success': True,
        'data': {
            'mes': mes,
            'ano': ano,
            'gastos': [g.to_dict() for g in gastos]
        }
    })


@relatorios_bp.route('/por-forma-pagamento', methods=['GET'])
def gastos_por_forma_pagamento():
    """Retorna gastos agrupados por forma de pagamento"""
    mes = request.args.get('mes', datetime.now().month, type=int)
    ano = request.args.get('ano', datetime.now().year, type=int)
    
    resultados = db.session.query(
        Gasto.forma_pagamento,
        func.sum(Gasto.valor).label('total'),
        func.count(Gasto.id).label('quantidade')
    ).filter(
        Gasto.tipo == 'despesa',
        extract('month', Gasto.data) == mes,
        extract('year', Gasto.data) == ano
    ).group_by(Gasto.forma_pagamento).all()
    
    total_geral = sum(r.total for r in resultados) if resultados else 0
    
    dados = []
    for r in resultados:
        dados.append({
            'forma_pagamento': r.forma_pagamento or 'Não informado',
            'total': float(r.total),
            'quantidade': r.quantidade,
            'percentual': round((float(r.total) / float(total_geral)) * 100, 2) if total_geral > 0 else 0
        })
    
    dados.sort(key=lambda x: x['total'], reverse=True)
    
    return jsonify({
        'success': True,
        'data': {
            'mes': mes,
            'ano': ano,
            'total_geral': float(total_geral),
            'formas_pagamento': dados
        }
    })
