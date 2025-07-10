import os
import sys
# DON'T CHANGE THIS !!!
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from flask import Flask, send_from_directory
from flask_cors import CORS

# Importar modelos
from src.models.user import db
from src.models.lancamento import Lancamento
from src.models.orcamento import Orcamento, ServicoOrcamento
from src.models.contrato import Contrato
from src.models.tarefa import Tarefa

# Importar rotas
from src.routes.user import user_bp
from src.routes.auth import auth_bp
from src.routes.lancamentos import lancamentos_bp
from src.routes.orcamentos import orcamentos_bp
from src.routes.contratos import contratos_bp
from src.routes.tarefas import tarefas_bp

app = Flask(__name__, static_folder=os.path.join(os.path.dirname(__file__), 'static'))

# Configurações
app.config['SECRET_KEY'] = 'orbisx_secret_key_2025'
app.config['SQLALCHEMY_DATABASE_URI'] = f"sqlite:///{os.path.join(os.path.dirname(__file__), 'database', 'app.db')}"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Configurar CORS para permitir requisições do frontend
CORS(app, supports_credentials=True)

# Registrar blueprints
app.register_blueprint(user_bp, url_prefix='/api')
app.register_blueprint(auth_bp, url_prefix='/api')
app.register_blueprint(lancamentos_bp, url_prefix='/api')
app.register_blueprint(orcamentos_bp, url_prefix='/api')
app.register_blueprint(contratos_bp, url_prefix='/api')
app.register_blueprint(tarefas_bp, url_prefix='/api')

# Inicializar banco de dados
db.init_app(app)
with app.app_context():
    db.create_all()

@app.route('/', defaults={'path': ''})
@app.route('/<path:path>')
def serve(path):
    static_folder_path = app.static_folder
    if static_folder_path is None:
        return "Static folder not configured", 404

    if path != "" and os.path.exists(os.path.join(static_folder_path, path)):
        return send_from_directory(static_folder_path, path)
    else:
        index_path = os.path.join(static_folder_path, 'index.html')
        if os.path.exists(index_path):
            return send_from_directory(static_folder_path, 'index.html')
        else:
            return "index.html not found", 404

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=False)
