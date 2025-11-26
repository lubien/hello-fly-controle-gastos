from datetime import datetime
from app import db


class Categoria(db.Model):
    """Modelo para categorias de gastos"""
    __tablename__ = 'categorias'
    
    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(100), nullable=False, unique=True)
    descricao = db.Column(db.String(255))
    cor = db.Column(db.String(7), default='#007bff')  # Cor hexadecimal
    icone = db.Column(db.String(50), default='📦')
    ativo = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relacionamento com gastos
    gastos = db.relationship('Gasto', backref='categoria', lazy='dynamic')
    
    def to_dict(self):
        return {
            'id': self.id,
            'nome': self.nome,
            'descricao': self.descricao,
            'cor': self.cor,
            'icone': self.icone,
            'ativo': self.ativo,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }
    
    def __repr__(self):
        return f'<Categoria {self.nome}>'


class Gasto(db.Model):
    """Modelo para gastos"""
    __tablename__ = 'gastos'
    
    id = db.Column(db.Integer, primary_key=True)
    descricao = db.Column(db.String(255), nullable=False)
    valor = db.Column(db.Numeric(10, 2), nullable=False)
    data = db.Column(db.Date, nullable=False, default=datetime.utcnow().date)
    categoria_id = db.Column(db.Integer, db.ForeignKey('categorias.id'), nullable=True)
    tipo = db.Column(db.String(20), default='despesa')  # 'despesa' ou 'receita'
    forma_pagamento = db.Column(db.String(50))  # Cartão, Dinheiro, PIX, etc.
    observacao = db.Column(db.Text)
    comprovante = db.Column(db.String(255))  # Caminho para arquivo de comprovante
    recorrente = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def to_dict(self):
        return {
            'id': self.id,
            'descricao': self.descricao,
            'valor': float(self.valor),
            'data': self.data.isoformat() if self.data else None,
            'categoria_id': self.categoria_id,
            'categoria': self.categoria.to_dict() if self.categoria else None,
            'tipo': self.tipo,
            'forma_pagamento': self.forma_pagamento,
            'observacao': self.observacao,
            'comprovante': self.comprovante,
            'recorrente': self.recorrente,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }
    
    def __repr__(self):
        return f'<Gasto {self.descricao} - R${self.valor}>'


class OrcamentoMensal(db.Model):
    """Modelo para orçamento mensal por categoria"""
    __tablename__ = 'orcamentos_mensais'
    
    id = db.Column(db.Integer, primary_key=True)
    categoria_id = db.Column(db.Integer, db.ForeignKey('categorias.id'), nullable=False)
    mes = db.Column(db.Integer, nullable=False)  # 1-12
    ano = db.Column(db.Integer, nullable=False)
    valor_limite = db.Column(db.Numeric(10, 2), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relacionamento
    categoria = db.relationship('Categoria', backref='orcamentos')
    
    # Índice único para evitar duplicatas
    __table_args__ = (
        db.UniqueConstraint('categoria_id', 'mes', 'ano', name='unique_orcamento_categoria_mes_ano'),
    )
    
    def to_dict(self):
        return {
            'id': self.id,
            'categoria_id': self.categoria_id,
            'categoria': self.categoria.to_dict() if self.categoria else None,
            'mes': self.mes,
            'ano': self.ano,
            'valor_limite': float(self.valor_limite),
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }
    
    def __repr__(self):
        return f'<OrcamentoMensal {self.mes}/{self.ano} - R${self.valor_limite}>'
