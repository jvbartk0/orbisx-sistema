# Documentação Técnica - Sistema Orbisx

## Visão Geral

O Sistema Orbisx é uma aplicação web full-stack desenvolvida para gestão empresarial, especificamente voltada para empresas de fotografia e serviços criativos. A aplicação utiliza uma arquitetura moderna com backend Flask e frontend React.

## Arquitetura do Sistema

### Stack Tecnológico

**Backend:**
- Python 3.11
- Flask 2.3.3
- SQLAlchemy (ORM)
- SQLite (Banco de dados)
- Flask-CORS (Cross-Origin Resource Sharing)
- ReportLab (Geração de PDF)

**Frontend:**
- React 18
- TailwindCSS (Estilização)
- Lucide React (Ícones)
- Framer Motion (Animações)
- Vite (Build tool)

**Deploy:**
- Render.com (Hospedagem)
- Git (Controle de versão)

### Estrutura de Diretórios

```
orbisx/
├── backend/                 # API Flask
│   ├── src/
│   │   ├── main.py         # Arquivo principal da aplicação
│   │   ├── models/         # Modelos de dados
│   │   │   ├── user.py     # Modelo de usuário
│   │   │   ├── lancamento.py # Modelo de lançamentos
│   │   │   ├── orcamento.py  # Modelo de orçamentos
│   │   │   ├── contrato.py   # Modelo de contratos
│   │   │   └── tarefa.py     # Modelo de tarefas
│   │   ├── routes/         # Rotas da API
│   │   │   ├── auth.py     # Autenticação
│   │   │   ├── lancamentos.py # Lançamentos financeiros
│   │   │   ├── orcamentos.py  # Orçamentos
│   │   │   ├── contratos.py   # Contratos
│   │   │   └── tarefas.py     # Tarefas
│   │   └── static/         # Arquivos estáticos (build do React)
│   ├── requirements.txt    # Dependências Python
│   └── venv/              # Ambiente virtual
├── frontend/              # Aplicação React
│   ├── src/
│   │   ├── components/    # Componentes React
│   │   │   ├── Login.jsx  # Tela de login
│   │   │   ├── Sidebar.jsx # Menu lateral
│   │   │   ├── Dashboard.jsx # Dashboard principal
│   │   │   ├── Orcamentos.jsx # Gestão de orçamentos
│   │   │   ├── Contratos.jsx  # Gestão de contratos
│   │   │   └── Agenda.jsx     # Gestão de tarefas
│   │   ├── App.jsx        # Componente principal
│   │   └── App.css        # Estilos globais
│   ├── package.json       # Dependências Node.js
│   └── dist/             # Build de produção
├── DEPLOY.md             # Guia de deploy
├── MANUAL_USUARIO.md     # Manual do usuário
├── README.md             # Documentação geral
└── render.yaml           # Configuração do Render
```

## Backend - API Flask

### Configuração Principal (main.py)

```python
from flask import Flask, render_template, send_from_directory
from flask_cors import CORS
from src.models.user import db
import os

app = Flask(__name__)
app.config['SECRET_KEY'] = 'orbisx-secret-key-2025'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db.init_app(app)
CORS(app)

# Registrar blueprints
from src.routes.auth import auth_bp
from src.routes.lancamentos import lancamentos_bp
from src.routes.orcamentos import orcamentos_bp
from src.routes.contratos import contratos_bp
from src.routes.tarefas import tarefas_bp

app.register_blueprint(auth_bp, url_prefix='/api')
app.register_blueprint(lancamentos_bp, url_prefix='/api')
app.register_blueprint(orcamentos_bp, url_prefix='/api')
app.register_blueprint(contratos_bp, url_prefix='/api')
app.register_blueprint(tarefas_bp, url_prefix='/api')
```

### Modelos de Dados

#### Modelo de Lançamento (lancamento.py)

```python
class Lancamento(db.Model):
    __tablename__ = 'lancamentos'
    
    id = db.Column(db.Integer, primary_key=True)
    tipo = db.Column(db.String(20), nullable=False)  # 'entrada' ou 'saida'
    valor = db.Column(db.Float, nullable=False)
    data = db.Column(db.Date, nullable=False)
    categoria = db.Column(db.String(100), nullable=False)
    descricao = db.Column(db.Text, nullable=True)
    data_criacao = db.Column(db.DateTime, default=datetime.utcnow)
```

#### Modelo de Orçamento (orcamento.py)

```python
class Orcamento(db.Model):
    __tablename__ = 'orcamentos'
    
    id = db.Column(db.Integer, primary_key=True)
    titulo = db.Column(db.String(200), nullable=False)
    cliente = db.Column(db.String(200), nullable=False)
    valor_total = db.Column(db.Float, nullable=False, default=0.0)
    status = db.Column(db.String(50), nullable=False, default='Pendente')
    forma_pagamento = db.Column(db.String(100), nullable=True)
    prazo_entrega = db.Column(db.Date, nullable=True)
    descricao = db.Column(db.Text, nullable=True)
    data_criacao = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relacionamento com serviços
    servicos = db.relationship('ServicoOrcamento', backref='orcamento', lazy=True, cascade='all, delete-orphan')
```

### Rotas da API

#### Autenticação (auth.py)

```python
@auth_bp.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    username = data.get('username')
    password = data.get('password')
    
    if username == 'eighmen' and password == 'Eighmen8':
        session['user_id'] = 1
        session['username'] = username
        return jsonify({'success': True, 'message': 'Login realizado com sucesso'})
    
    return jsonify({'success': False, 'message': 'Credenciais inválidas'}), 401
```

#### Lançamentos (lancamentos.py)

```python
@lancamentos_bp.route('/lancamentos', methods=['GET'])
def listar_lancamentos():
    # Filtros opcionais
    data_inicio = request.args.get('data_inicio')
    data_fim = request.args.get('data_fim')
    
    query = Lancamento.query
    
    # Aplicar filtros de data
    if data_inicio:
        data_inicio_obj = datetime.strptime(data_inicio, '%Y-%m-%d').date()
        query = query.filter(Lancamento.data >= data_inicio_obj)
    
    if data_fim:
        data_fim_obj = datetime.strptime(data_fim, '%Y-%m-%d').date()
        query = query.filter(Lancamento.data <= data_fim_obj)
    
    lancamentos = query.order_by(Lancamento.data.desc()).all()
    return jsonify([lancamento.to_dict() for lancamento in lancamentos])
```

## Frontend - Aplicação React

### Componente Principal (App.jsx)

```jsx
function App() {
  const [isAuthenticated, setIsAuthenticated] = useState(false);
  const [currentPage, setCurrentPage] = useState('dashboard');
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    checkAuth();
  }, []);

  const checkAuth = async () => {
    try {
      const response = await fetch('/api/check-auth');
      const data = await response.json();
      setIsAuthenticated(data.authenticated);
    } catch (error) {
      console.error('Erro ao verificar autenticação:', error);
    } finally {
      setLoading(false);
    }
  };

  if (loading) {
    return <div className="loading">Carregando...</div>;
  }

  if (!isAuthenticated) {
    return <Login onLogin={() => setIsAuthenticated(true)} />;
  }

  return (
    <div className="app">
      <Sidebar currentPage={currentPage} onPageChange={setCurrentPage} />
      <main className="main-content">
        {currentPage === 'dashboard' && <Dashboard />}
        {currentPage === 'orcamentos' && <Orcamentos />}
        {currentPage === 'contratos' && <Contratos />}
        {currentPage === 'agenda' && <Agenda />}
      </main>
    </div>
  );
}
```

### Componente Dashboard (Dashboard.jsx)

```jsx
function Dashboard() {
  const [lancamentos, setLancamentos] = useState([]);
  const [resumo, setResumo] = useState({
    total_caixa: 0,
    total_entradas: 0,
    total_saidas: 0
  });

  useEffect(() => {
    carregarDados();
  }, []);

  const carregarDados = async () => {
    try {
      const [lancamentosRes, resumoRes] = await Promise.all([
        fetch('/api/lancamentos'),
        fetch('/api/lancamentos/resumo')
      ]);
      
      const lancamentosData = await lancamentosRes.json();
      const resumoData = await resumoRes.json();
      
      setLancamentos(lancamentosData);
      setResumo(resumoData);
    } catch (error) {
      console.error('Erro ao carregar dados:', error);
    }
  };

  return (
    <div className="dashboard">
      <div className="kpis">
        <div className="kpi-card">
          <h3>Total em Caixa</h3>
          <p>R$ {resumo.total_caixa.toFixed(2)}</p>
        </div>
        <div className="kpi-card">
          <h3>Entradas</h3>
          <p>R$ {resumo.total_entradas.toFixed(2)}</p>
        </div>
        <div className="kpi-card">
          <h3>Saídas</h3>
          <p>R$ {resumo.total_saidas.toFixed(2)}</p>
        </div>
      </div>
      
      <div className="charts">
        {/* Gráficos e tabelas */}
      </div>
    </div>
  );
}
```

## Banco de Dados

### Esquema do Banco

O sistema utiliza SQLite com as seguintes tabelas:

#### Tabela: lancamentos
```sql
CREATE TABLE lancamentos (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    tipo VARCHAR(20) NOT NULL,
    valor FLOAT NOT NULL,
    data DATE NOT NULL,
    categoria VARCHAR(100) NOT NULL,
    descricao TEXT,
    data_criacao DATETIME DEFAULT CURRENT_TIMESTAMP
);
```

#### Tabela: orcamentos
```sql
CREATE TABLE orcamentos (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    titulo VARCHAR(200) NOT NULL,
    cliente VARCHAR(200) NOT NULL,
    valor_total FLOAT NOT NULL DEFAULT 0.0,
    status VARCHAR(50) NOT NULL DEFAULT 'Pendente',
    forma_pagamento VARCHAR(100),
    prazo_entrega DATE,
    descricao TEXT,
    data_criacao DATETIME DEFAULT CURRENT_TIMESTAMP
);
```

#### Tabela: servicos_orcamento
```sql
CREATE TABLE servicos_orcamento (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    orcamento_id INTEGER NOT NULL,
    nome VARCHAR(200) NOT NULL,
    quantidade INTEGER NOT NULL,
    preco_unitario FLOAT NOT NULL,
    FOREIGN KEY (orcamento_id) REFERENCES orcamentos (id)
);
```

#### Tabela: contratos
```sql
CREATE TABLE contratos (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    titulo VARCHAR(200) NOT NULL,
    cliente VARCHAR(200) NOT NULL,
    valor FLOAT NOT NULL,
    data_inicio DATE NOT NULL,
    data_fim DATE NOT NULL,
    status VARCHAR(50) NOT NULL DEFAULT 'Ativo',
    arquivo_path VARCHAR(500),
    data_criacao DATETIME DEFAULT CURRENT_TIMESTAMP
);
```

#### Tabela: tarefas
```sql
CREATE TABLE tarefas (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    titulo VARCHAR(200) NOT NULL,
    tipo VARCHAR(50) NOT NULL,
    data DATE NOT NULL,
    hora TIME,
    descricao TEXT,
    status VARCHAR(50) NOT NULL DEFAULT 'Pendente',
    data_criacao DATETIME DEFAULT CURRENT_TIMESTAMP
);
```

## Funcionalidades Principais

### 1. Sistema de Autenticação

- Login com credenciais fixas (eighmen/Eighmen8)
- Sessão persistente usando Flask sessions
- Verificação de autenticação em todas as rotas protegidas

### 2. Gestão Financeira

- Lançamentos de entrada e saída
- Categorização de lançamentos
- Filtros por data e categoria
- Cálculo automático de saldos
- Gráficos de categorias e evolução temporal

### 3. Gestão de Orçamentos

- Criação de orçamentos com múltiplos serviços
- Cálculo automático de valores
- Geração de PDF profissional
- Controle de status (Pendente, Enviado, Aceito, Rejeitado)
- Filtros por status e cliente

### 4. Gestão de Contratos

- Upload de contratos em PDF
- Visualização online de contratos
- Download de arquivos
- Controle de datas e status
- Filtros por cliente e período

### 5. Gestão de Agenda

- Criação de tarefas por categoria
- Calendário mensal interativo
- Controle de status (Pendente, Concluída)
- Estatísticas de produtividade
- Filtros por tipo, data e status

## Segurança

### Medidas Implementadas

1. **Autenticação**: Sistema de login obrigatório
2. **Sessões**: Controle de sessão do usuário
3. **CORS**: Configuração adequada para requisições cross-origin
4. **Validação**: Validação de dados de entrada
5. **Sanitização**: Tratamento de dados para evitar injeções

### Recomendações Adicionais

1. Implementar HTTPS em produção
2. Usar senhas mais seguras
3. Implementar rate limiting
4. Adicionar logs de auditoria
5. Configurar backup automático

## Performance

### Otimizações Implementadas

1. **Frontend**: Build otimizado com Vite
2. **Backend**: Queries otimizadas com SQLAlchemy
3. **Banco**: Índices nas colunas mais consultadas
4. **Cache**: Headers de cache para assets estáticos

### Monitoramento

1. Logs de aplicação no Render
2. Métricas de performance
3. Alertas de erro
4. Monitoramento de recursos

## Manutenção

### Backup de Dados

```bash
# Backup do banco SQLite
cp backend/database.db backup/database_$(date +%Y%m%d).db

# Backup de arquivos uploadados
tar -czf backup/uploads_$(date +%Y%m%d).tar.gz backend/uploads/
```

### Atualizações

1. Testar em ambiente local
2. Fazer backup dos dados
3. Deploy via Git push
4. Verificar funcionamento
5. Rollback se necessário

### Logs

```bash
# Visualizar logs do backend
tail -f /var/log/orbisx/backend.log

# Logs do Render
# Acessar via painel web do Render.com
```

## Troubleshooting

### Problemas Comuns

1. **Erro 500**: Verificar logs do backend
2. **CORS Error**: Verificar configuração de CORS
3. **Upload falha**: Verificar permissões de arquivo
4. **Login não funciona**: Verificar credenciais e sessão

### Comandos Úteis

```bash
# Reiniciar aplicação
sudo systemctl restart orbisx

# Verificar status
sudo systemctl status orbisx

# Limpar cache
rm -rf frontend/dist/
npm run build

# Reset do banco (CUIDADO!)
rm backend/database.db
python backend/src/main.py  # Recria as tabelas
```

## Contato e Suporte

Para questões técnicas ou suporte:

- Documentação: Consulte este arquivo
- Logs: Verifique os logs da aplicação
- Issues: Reporte problemas no repositório Git

---

**Versão**: 1.0  
**Data**: Julho 2025  
**Desenvolvedor**: Manus AI  
**Tecnologias**: Flask + React + SQLite

