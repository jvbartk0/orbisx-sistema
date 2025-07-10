# Guia de Deploy do Sistema Orbisx no Render.com

Este guia fornece instruções detalhadas e testadas para fazer o deploy do sistema Orbisx no Render.com, garantindo que tanto o backend Flask quanto o frontend React funcionem corretamente em produção.

## Pré-requisitos

Antes de iniciar o deploy, certifique-se de que você tem:

- Conta no Render.com (gratuita ou paga)
- Repositório Git com o código do sistema Orbisx
- Acesso ao painel de controle do Render.com

## Estrutura do Projeto

O sistema Orbisx está organizado da seguinte forma:

```
orbisx/
├── backend/          # API Flask
│   ├── src/
│   │   ├── main.py   # Arquivo principal
│   │   ├── models/   # Modelos do banco
│   │   └── routes/   # Rotas da API
│   ├── requirements.txt
│   └── venv/
├── frontend/         # App React
│   ├── src/
│   ├── package.json
│   └── dist/         # Build de produção
├── render.yaml       # Configuração do Render
└── Procfile         # Comando de inicialização
```

## Parte 1: Deploy do Backend (Flask)

### 1.1 Configurações do Serviço Backend

No painel do Render.com, crie um novo **Web Service** com as seguintes configurações:

**Configurações Básicas:**
- **Name**: `orbisx-backend`
- **Environment**: `Python 3`
- **Region**: `Oregon (US West)` ou mais próxima
- **Branch**: `main` (ou sua branch principal)

**Configurações de Build e Deploy:**
- **Root Directory**: `backend`
- **Build Command**: `pip install -r requirements.txt`
- **Start Command**: `python src/main.py`

**Variáveis de Ambiente:**
```
FLASK_ENV=production
FLASK_APP=src/main.py
PORT=5000
```

**Configurações de Plano:**
- **Plan**: `Free` (para testes) ou `Starter` (para produção)

### 1.2 Configuração do Banco de Dados SQLite

O SQLite não requer configuração especial no Render, pois é um banco de dados baseado em arquivo. O arquivo `database.db` será criado automaticamente na primeira execução.

**Importante**: Em produção, considere usar PostgreSQL para melhor performance e persistência de dados.

### 1.3 Configurações Específicas do Flask

Certifique-se de que o arquivo `src/main.py` contenha as configurações corretas para produção:

```python
if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=False)
```

## Parte 2: Deploy do Frontend (React)

### 2.1 Preparação do Build

Antes do deploy, construa o frontend localmente:

```bash
cd frontend
npm run build
```

### 2.2 Configurações do Serviço Frontend

Crie um novo **Static Site** no Render.com:

**Configurações Básicas:**
- **Name**: `orbisx-frontend`
- **Root Directory**: `frontend`
- **Build Command**: `npm run build`
- **Publish Directory**: `dist`

**Configurações de Build:**
- **Node Version**: `18` ou superior
- **Build Command**: `npm ci && npm run build`

### 2.3 Configuração de Proxy para API

No arquivo `vite.config.js`, configure o proxy para apontar para o backend em produção:

```javascript
export default defineConfig({
  plugins: [react()],
  server: {
    proxy: {
      '/api': {
        target: 'https://orbisx-backend.onrender.com',
        changeOrigin: true,
        secure: true
      }
    }
  }
})
```

## Parte 3: Configuração de Comunicação Frontend-Backend

### 3.1 CORS no Backend

Certifique-se de que o CORS está configurado corretamente no Flask:

```python
from flask_cors import CORS

app = Flask(__name__)
CORS(app, origins=['https://orbisx-frontend.onrender.com'])
```

### 3.2 URLs da API no Frontend

Atualize as URLs da API no frontend para apontar para o backend em produção:

```javascript
const API_BASE_URL = 'https://orbisx-backend.onrender.com/api';
```

## Parte 4: Configurações Avançadas

### 4.1 Arquivo render.yaml (Opcional)

Para deploy automatizado, use o arquivo `render.yaml`:

```yaml
services:
  - type: web
    name: orbisx-backend
    env: python
    buildCommand: pip install -r requirements.txt
    startCommand: python src/main.py
    envVars:
      - key: FLASK_ENV
        value: production
      - key: PORT
        value: 5000

  - type: web
    name: orbisx-frontend
    env: static
    buildCommand: npm ci && npm run build
    staticPublishPath: ./dist
```

### 4.2 Configurações de Domínio Personalizado

Para usar um domínio personalizado:

1. Acesse as configurações do serviço
2. Vá para "Custom Domains"
3. Adicione seu domínio
4. Configure os registros DNS conforme instruído

## Parte 5: Verificação e Testes

### 5.1 Checklist de Verificação

Após o deploy, verifique:

- [ ] Backend está respondendo em `https://orbisx-backend.onrender.com`
- [ ] Frontend está carregando em `https://orbisx-frontend.onrender.com`
- [ ] Login funciona corretamente
- [ ] APIs estão retornando dados
- [ ] Banco de dados está funcionando
- [ ] Upload de arquivos funciona (se aplicável)

### 5.2 Testes de Funcionalidade

Teste todas as funcionalidades principais:

1. **Login**: Teste com credenciais `eighmen/Eighmen8`
2. **Dashboard**: Verifique KPIs e gráficos
3. **Lançamentos**: Teste criação e listagem
4. **Orçamentos**: Teste criação e geração de PDF
5. **Contratos**: Teste upload de arquivos
6. **Agenda**: Teste criação de tarefas

## Parte 6: Monitoramento e Logs

### 6.1 Visualização de Logs

Para visualizar logs em tempo real:

1. Acesse o painel do serviço no Render
2. Clique na aba "Logs"
3. Monitore erros e atividades

### 6.2 Configuração de Alertas

Configure alertas para:
- Falhas de deploy
- Erros de aplicação
- Uso excessivo de recursos

## Parte 7: Solução de Problemas Comuns

### 7.1 Erro 500 no Backend

**Causa**: Geralmente relacionado a configurações de banco ou variáveis de ambiente.

**Solução**:
1. Verifique os logs do backend
2. Confirme variáveis de ambiente
3. Teste localmente primeiro

### 7.2 Frontend não carrega

**Causa**: Problemas de build ou configuração de proxy.

**Solução**:
1. Verifique o build local
2. Confirme configurações de proxy
3. Teste URLs da API

### 7.3 Problemas de CORS

**Causa**: Configuração incorreta de CORS no backend.

**Solução**:
1. Atualize configurações de CORS
2. Adicione domínio do frontend nas origens permitidas
3. Redeploy o backend

## Parte 8: Manutenção e Atualizações

### 8.1 Deploy de Atualizações

Para atualizar o sistema:

1. Faça push das alterações para o repositório
2. O Render fará deploy automaticamente
3. Monitore os logs durante o deploy

### 8.2 Backup de Dados

Para backup do banco SQLite:

1. Acesse o shell do serviço
2. Faça download do arquivo `database.db`
3. Armazene em local seguro

### 8.3 Escalabilidade

Para melhor performance em produção:

1. Upgrade para planos pagos
2. Configure PostgreSQL
3. Implemente cache Redis
4. Configure CDN para assets estáticos

## Conclusão

Este guia fornece todas as informações necessárias para fazer o deploy do sistema Orbisx no Render.com. Siga os passos cuidadosamente e teste todas as funcionalidades após o deploy.

Para suporte adicional, consulte a documentação oficial do Render.com ou entre em contato com o suporte técnico.

---

**Última atualização**: Julho 2025  
**Versão do Sistema**: Orbisx v1.0  
**Plataforma**: Render.com

