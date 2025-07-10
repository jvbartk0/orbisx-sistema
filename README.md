# Sistema Orbisx - Gestão Empresarial

Sistema de gestão empresarial moderno e completo para PMEs, desenvolvido com React e Flask.

## Características

- **Frontend**: React com TailwindCSS, Lucide Icons e Framer Motion
- **Backend**: Flask com SQLAlchemy e SQLite
- **Design**: Interface escura moderna com detalhes roxos
- **Responsivo**: Funciona perfeitamente em desktop, tablet e mobile
- **Funcionalidades**: Dashboard, Orçamentos, Contratos e Agenda

## Estrutura do Projeto

```
orbisx/
├── frontend/          # Aplicação React
├── backend/           # API Flask
├── README.md          # Este arquivo
└── DEPLOY.md          # Guia de deploy para Render.com
```

## Desenvolvimento Local

### Backend
```bash
cd backend
source venv/bin/activate
python src/main.py
```

### Frontend
```bash
cd frontend
pnpm run dev
```

## Deploy

Consulte o arquivo `DEPLOY.md` para instruções detalhadas de deploy no Render.com.

## Credenciais de Acesso

- **Usuário**: eighmen
- **Senha**: Eighmen8

## Funcionalidades

### Dashboard
- Visão geral financeira
- Lançamentos de entrada e saída
- Gráficos e relatórios
- Filtros por data

### Orçamentos
- Criação de propostas
- Geração de PDF
- Controle de status
- Filtros avançados

### Contratos
- Upload de documentos
- Controle de vigência
- Download de arquivos
- Organização por cliente

### Agenda
- Calendário mensal
- Tarefas por categoria
- Estatísticas de produtividade
- Controle de compromissos

## Tecnologias

- React 18
- TailwindCSS
- Lucide Icons
- Framer Motion
- Flask
- SQLAlchemy
- SQLite

