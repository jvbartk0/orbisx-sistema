from src.models.user import db
from datetime import datetime

class Tarefa(db.Model):
    __tablename__ = 'tarefas'
    
    id = db.Column(db.Integer, primary_key=True)
    titulo = db.Column(db.String(200), nullable=False)
    tipo = db.Column(db.String(50), nullable=False)  # 'captacao', 'edicao', 'reuniao'
    data = db.Column(db.Date, nullable=False)
    horario = db.Column(db.Time, nullable=True)
    cliente = db.Column(db.String(200), nullable=True)
    local = db.Column(db.String(200), nullable=True)
    descricao = db.Column(db.Text, nullable=True)
    concluida = db.Column(db.Boolean, default=False)
    data_criacao = db.Column(db.DateTime, default=datetime.utcnow)
    
    def __repr__(self):
        return f'<Tarefa {self.titulo} - {self.tipo}>'
    
    def to_dict(self):
        return {
            'id': self.id,
            'titulo': self.titulo,
            'tipo': self.tipo,
            'data': self.data.isoformat() if self.data else None,
            'horario': self.horario.strftime('%H:%M') if self.horario else None,
            'cliente': self.cliente,
            'local': self.local,
            'descricao': self.descricao,
            'concluida': self.concluida,
            'data_criacao': self.data_criacao.isoformat() if self.data_criacao else None
        }

