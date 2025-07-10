from src.models.user import db
from datetime import datetime

class Contrato(db.Model):
    __tablename__ = 'contratos'
    
    id = db.Column(db.Integer, primary_key=True)
    titulo = db.Column(db.String(200), nullable=False)
    cliente = db.Column(db.String(200), nullable=False)
    valor = db.Column(db.Float, nullable=False)
    data_inicio = db.Column(db.Date, nullable=False)
    data_fim = db.Column(db.Date, nullable=False)
    observacoes = db.Column(db.Text, nullable=True)
    nome_arquivo = db.Column(db.String(255), nullable=True)
    caminho_arquivo = db.Column(db.String(500), nullable=True)
    data_upload = db.Column(db.DateTime, default=datetime.utcnow)
    
    def __repr__(self):
        return f'<Contrato {self.titulo} - {self.cliente}>'
    
    def to_dict(self):
        return {
            'id': self.id,
            'titulo': self.titulo,
            'cliente': self.cliente,
            'valor': self.valor,
            'data_inicio': self.data_inicio.isoformat() if self.data_inicio else None,
            'data_fim': self.data_fim.isoformat() if self.data_fim else None,
            'observacoes': self.observacoes,
            'nome_arquivo': self.nome_arquivo,
            'data_upload': self.data_upload.isoformat() if self.data_upload else None
        }

