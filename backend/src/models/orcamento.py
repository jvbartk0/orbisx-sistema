from src.models.user import db
from datetime import datetime

class Orcamento(db.Model):
    __tablename__ = 'orcamentos'
    
    id = db.Column(db.Integer, primary_key=True)
    titulo = db.Column(db.String(200), nullable=False)
    cliente = db.Column(db.String(200), nullable=False)
    descricao = db.Column(db.Text, nullable=True)
    forma_pagamento = db.Column(db.String(100), nullable=True)
    prazo_entrega = db.Column(db.Date, nullable=True)
    status = db.Column(db.String(20), default='pendente')  # pendente, enviado, aceito, rejeitado
    data_criacao = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relacionamento com serviços
    servicos = db.relationship('ServicoOrcamento', backref='orcamento', lazy=True, cascade='all, delete-orphan')
    
    def __repr__(self):
        return f'<Orcamento {self.titulo} - {self.cliente}>'
    
    def calcular_total(self):
        return sum(servico.quantidade * servico.preco_unitario for servico in self.servicos)
    
    def to_dict(self):
        return {
            'id': self.id,
            'titulo': self.titulo,
            'cliente': self.cliente,
            'descricao': self.descricao,
            'forma_pagamento': self.forma_pagamento,
            'prazo_entrega': self.prazo_entrega.isoformat() if self.prazo_entrega else None,
            'status': self.status,
            'data_criacao': self.data_criacao.isoformat() if self.data_criacao else None,
            'valor_total': self.calcular_total(),
            'servicos': [servico.to_dict() for servico in self.servicos]
        }

class ServicoOrcamento(db.Model):
    __tablename__ = 'servicos_orcamento'
    
    id = db.Column(db.Integer, primary_key=True)
    orcamento_id = db.Column(db.Integer, db.ForeignKey('orcamentos.id'), nullable=False)
    nome = db.Column(db.String(200), nullable=False)
    quantidade = db.Column(db.Integer, nullable=False, default=1)
    preco_unitario = db.Column(db.Float, nullable=False)
    
    def __repr__(self):
        return f'<ServicoOrcamento {self.nome}>'
    
    def to_dict(self):
        return {
            'id': self.id,
            'nome': self.nome,
            'quantidade': self.quantidade,
            'preco_unitario': self.preco_unitario,
            'subtotal': self.quantidade * self.preco_unitario
        }

