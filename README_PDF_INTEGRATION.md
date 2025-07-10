# Integração de Geração de PDF - Orbisx Sistema

## Modificações Realizadas

### 1. Backend - Rota de Geração de PDF
**Arquivo modificado:** `backend/src/routes/orcamentos.py`

- Adicionada nova rota `/api/orcamentos/<int:orcamento_id>/pdf`
- Implementada função `gerar_pdf_orcamento()` que:
  - Busca os dados do orçamento no banco de dados
  - Gera PDF profissional usando ReportLab
  - Retorna PDF com nome padronizado `orcamento-n[número].pdf`
  - Layout baseado no modelo fornecido pelo usuário
  - Inclui dados da empresa "Eighmen" (fixo)
  - Inclui todos os dados do cliente e itens do orçamento

### 2. Frontend - Script de Interceptação
**Arquivo criado:** `backend/src/static/assets/pdf-generator.js`

- Script JavaScript que intercepta cliques nos botões de download
- Substitui a funcionalidade original por chamada à nova rota de PDF
- Usa MutationObserver para detectar novos elementos dinamicamente
- Faz download automático do PDF gerado

### 3. HTML - Inclusão do Script
**Arquivo modificado:** `backend/src/static/index.html`

- Adicionada tag `<script>` para carregar o `pdf-generator.js`
- Script carregado após os assets principais

### 4. Configuração do Servidor
**Arquivo modificado:** `backend/src/main.py`

- Alterada porta padrão de 5000 para 5002 (para evitar conflitos)

## Como Funciona

1. **Usuário clica no botão "Baixar"** de um orçamento
2. **Script intercepta o clique** e previne a ação original
3. **Extrai o ID do orçamento** do elemento HTML
4. **Faz requisição para** `/api/orcamentos/{id}/pdf`
5. **Backend gera PDF** com dados do banco
6. **Download automático** do arquivo `orcamento-n{id}.pdf`

## Estrutura do PDF Gerado

- **Cabeçalho:** Logo e dados da empresa "Eighmen"
- **Informações do Orçamento:** Número, data, validade
- **Dados do Cliente:** Nome, telefone, email, CPF, endereço
- **Tabela de Itens:** Descrição, quantidade, valor unitário, subtotal
- **Totais:** Subtotal, desconto, total final
- **Observações:** Forma de pagamento e outras informações
- **Rodapé:** Assinaturas da empresa e cliente

## Dependências Adicionais

- **ReportLab:** Para geração de PDF (já incluído no requirements.txt)
- **Flask-CORS:** Para permitir requisições do frontend (já incluído)

## Como Executar

1. **Navegar para o diretório backend:**
   ```bash
   cd backend
   ```

2. **Ativar ambiente virtual:**
   ```bash
   source venv/bin/activate
   ```

3. **Executar servidor:**
   ```bash
   python src/main.py
   ```

4. **Acessar aplicação:**
   ```
   http://localhost:5002
   ```

## Observações Importantes

- **Mexeu apenas no necessário:** Não alterou a estrutura original do projeto
- **Compatível:** Funciona com o sistema existente sem quebrar funcionalidades
- **Interceptação inteligente:** Detecta automaticamente novos botões de download
- **PDF profissional:** Layout limpo e organizado conforme solicitado
- **Nome padronizado:** Arquivos seguem padrão `orcamento-n{número}.pdf`

## Arquivos Modificados/Criados

```
backend/src/routes/orcamentos.py          (MODIFICADO)
backend/src/static/assets/pdf-generator.js (CRIADO)
backend/src/static/index.html              (MODIFICADO)
backend/src/main.py                        (MODIFICADO)
README_PDF_INTEGRATION.md                 (CRIADO)
```

A integração foi realizada de forma mínima e não invasiva, mantendo toda a funcionalidade original do sistema.

