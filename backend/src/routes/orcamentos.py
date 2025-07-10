from flask import Blueprint, request, jsonify, send_file
from datetime import datetime
from src.models.user import db
from src.models.orcamento import Orcamento, ServicoOrcamento

from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import cm
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Image
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT
import io
import os

orcamentos_bp = Blueprint("orcamentos", __name__)

@orcamentos_bp.route("/orcamentos", methods=["GET"])
def listar_orcamentos():
    try:
        # Filtros opcionais
        status = request.args.get("status")
        cliente = request.args.get("cliente")
        texto = request.args.get("texto")
        
        query = Orcamento.query
        
        # Aplicar filtros
        if status:
            query = query.filter(Orcamento.status == status)
        
        if cliente:
            query = query.filter(Orcamento.cliente.ilike(f"%{cliente}%"))
        
        if texto:
            query = query.filter(
                db.or_(
                    Orcamento.titulo.ilike(f"%{texto}%"),
                    Orcamento.cliente.ilike(f"%{texto}%"),
                    Orcamento.descricao.ilike(f"%{texto}%")
                )
            )
        
        orcamentos = query.order_by(Orcamento.data_criacao.desc()).all()
        
        return jsonify({
            "orcamentos": [orcamento.to_dict() for orcamento in orcamentos]
        }), 200
        
    except Exception as e:
        return jsonify({"error": "Erro interno do servidor"}), 500

@orcamentos_bp.route("/orcamentos", methods=["POST"])
def criar_orcamento():
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({"error": "Dados não fornecidos"}), 400
        
        # Validações obrigatórias
        titulo = data.get("titulo", "").strip()
        cliente = data.get("cliente", "").strip()
        descricao = data.get("descricao", "").strip()
        forma_pagamento = data.get("forma_pagamento", "").strip()
        prazo_entrega = data.get("prazo_entrega", "").strip()
        servicos = data.get("servicos", [])
        
        if not titulo:
            return jsonify({"error": "Título é obrigatório"}), 400
        
        if not cliente:
            return jsonify({"error": "Cliente é obrigatório"}), 400
        
        if not servicos or len(servicos) == 0:
            return jsonify({"error": "Pelo menos um serviço é obrigatório"}), 400
        
        # Converter data se fornecida
        prazo_obj = None
        if prazo_entrega:
            try:
                prazo_obj = datetime.strptime(prazo_entrega, "%Y-%m-%d").date()
            except ValueError:
                return jsonify({"error": "Formato de data inválido para prazo de entrega"}), 400
        
        # Criar novo orçamento
        novo_orcamento = Orcamento(
            titulo=titulo,
            cliente=cliente,
            descricao=descricao,
            forma_pagamento=forma_pagamento,
            prazo_entrega=prazo_obj
        )
        
        db.session.add(novo_orcamento)
        db.session.flush()  # Para obter o ID
        
        # Adicionar serviços
        for servico_data in servicos:
            nome = servico_data.get("nome", "").strip()
            quantidade = servico_data.get("quantidade", 1)
            preco_unitario = servico_data.get("preco_unitario", 0)
            
            if not nome:
                return jsonify({"error": "Nome do serviço é obrigatório"}), 400
            
            if quantidade <= 0:
                return jsonify({"error": "Quantidade deve ser maior que zero"}), 400
            
            if preco_unitario <= 0:
                return jsonify({"error": "Preço unitário deve ser maior que zero"}), 400
            
            novo_servico = ServicoOrcamento(
                orcamento_id=novo_orcamento.id,
                nome=nome,
                quantidade=int(quantidade),
                preco_unitario=float(preco_unitario)
            )
            
            db.session.add(novo_servico)
        
        db.session.commit()
        
        return jsonify({
            "success": True,
            "message": "Orçamento criado com sucesso",
            "orcamento": novo_orcamento.to_dict()
        }), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": "Erro interno do servidor"}), 500

@orcamentos_bp.route("/orcamentos/<int:orcamento_id>/status", methods=["PUT"])
def atualizar_status(orcamento_id):
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({"error": "Dados não fornecidos"}), 400
        
        novo_status = data.get("status", "").strip()
        
        if novo_status not in ["pendente", "enviado", "aceito", "rejeitado"]:
            return jsonify({"error": "Status inválido"}), 400
        
        orcamento = Orcamento.query.get(orcamento_id)
        
        if not orcamento:
            return jsonify({"error": "Orçamento não encontrado"}), 404
        
        orcamento.status = novo_status
        db.session.commit()
        
        return jsonify({
            "success": True,
            "message": "Status atualizado com sucesso",
            "orcamento": orcamento.to_dict()
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": "Erro interno do servidor"}), 500

@orcamentos_bp.route("/orcamentos/<int:orcamento_id>", methods=["GET"])
def obter_orcamento(orcamento_id):
    try:
        orcamento = Orcamento.query.get(orcamento_id)
        
        if not orcamento:
            return jsonify({"error": "Orçamento não encontrado"}), 404
        
        return jsonify({
            "orcamento": orcamento.to_dict()
        }), 200
        
    except Exception as e:
        return jsonify({"error": "Erro interno do servidor"}), 500

@orcamentos_bp.route("/orcamentos/clientes", methods=["GET"])
def listar_clientes():
    try:
        # Buscar clientes únicos
        clientes = db.session.query(Orcamento.cliente).distinct().all()
        clientes_list = [cliente[0] for cliente in clientes if cliente[0]]
        
        return jsonify({
            "clientes": sorted(clientes_list)
        }), 200
        
    except Exception as e:
        return jsonify({"error": "Erro interno do servidor"}), 500

@orcamentos_bp.route("/orcamentos/<int:orcamento_id>/gerar-pdf", methods=["GET"])
def gerar_pdf_orcamento(orcamento_id):
    try:
        orcamento = Orcamento.query.get(orcamento_id)
        
        if not orcamento:
            return jsonify({"error": "Orçamento não encontrado"}), 404
            
        # Criar buffer para o PDF
        buffer = io.BytesIO()
        
        # Configurar documento
        doc = SimpleDocTemplate(
            buffer,
            pagesize=A4,
            rightMargin=2*cm,
            leftMargin=2*cm,
            topMargin=1.5*cm,
            bottomMargin=2*cm
        )
        
        # Estilos
        styles = getSampleStyleSheet()
        
        # Estilo para cabeçalho da empresa
        empresa_style = ParagraphStyle(
            'EmpresaStyle',
            parent=styles['Normal'],
            fontSize=14,
            fontName='Helvetica-Bold',
            alignment=TA_LEFT,
            spaceAfter=2
        )
        
        # Estilo para dados da empresa
        empresa_dados_style = ParagraphStyle(
            'EmpresaDadosStyle',
            parent=styles['Normal'],
            fontSize=9,
            fontName='Helvetica',
            alignment=TA_LEFT,
            leading=11
        )
        
        # Estilo para contato da empresa
        contato_style = ParagraphStyle(
            'ContatoStyle',
            parent=styles['Normal'],
            fontSize=9,
            fontName='Helvetica',
            alignment=TA_RIGHT,
            leading=11
        )
        
        # Estilo para títulos de seção
        secao_style = ParagraphStyle(
            'SecaoStyle',
            parent=styles['Normal'],
            fontSize=11,
            fontName='Helvetica-Bold',
            alignment=TA_LEFT,
            spaceAfter=8,
            spaceBefore=15
        )
        
        # Estilo normal
        normal_style = ParagraphStyle(
            'NormalStyle',
            parent=styles['Normal'],
            fontSize=10,
            fontName='Helvetica',
            alignment=TA_LEFT,
            leading=12
        )
        
        # Lista de elementos do PDF
        story = []
        
        # CABEÇALHO COM LOGO E DADOS DA EMPRESA
        header_data = [
            [
                Paragraph('●●●<br/>EIGHMEN', ParagraphStyle('LogoStyle', parent=styles['Normal'], fontSize=12, fontName='Helvetica-Bold', textColor=colors.HexColor('#2c3e50'))),
                Paragraph('Eighmen<br/>CNPJ: 00.000.000/0001-00<br/>Rua Exemplo, nº 123, Bairro<br/>Cidade - Estado, CEP 00000-000', empresa_dados_style),
                Paragraph('(11) 99999-9999<br/>contato@eighmen.com.br<br/>www.eighmen.com.br', contato_style)
            ]
        ]
        
        header_table = Table(header_data, colWidths=[4*cm, 8*cm, 5*cm])
        header_table.setStyle(TableStyle([
            ('VALIGN', (0, 0), (-1, -1), 'TOP'),
            ('LEFTPADDING', (0, 0), (-1, -1), 0),
            ('RIGHTPADDING', (0, 0), (-1, -1), 0),
            ('TOPPADDING', (0, 0), (-1, -1), 0),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 10),
        ]))
        
        story.append(header_table)
        story.append(Spacer(1, 20))
        
        # INFORMAÇÕES DO ORÇAMENTO
        numero_orcamento = orcamento.id
        data_orcamento = orcamento.data_criacao.strftime('%d/%m/%Y') if orcamento.data_criacao else 'N/A'
        validade = '30' # Não há campo de validade no modelo atual, usando padrão
        
        info_data = [
            [
                f'Orçamento: {numero_orcamento}',
                f'Data: {data_orcamento}',
                f'Validade: {validade} dias'
            ]
        ]
        
        info_table = Table(info_data, colWidths=[6*cm, 5*cm, 6*cm])
        info_table.setStyle(TableStyle([
            ('FONTNAME', (0, 0), (-1, -1), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 11),
            ('ALIGN', (0, 0), (0, 0), 'LEFT'),
            ('ALIGN', (1, 0), (1, 0), 'CENTER'),
            ('ALIGN', (2, 0), (2, 0), 'RIGHT'),
            ('LEFTPADDING', (0, 0), (-1, -1), 0),
            ('RIGHTPADDING', (0, 0), (-1, -1), 0),
            ('TOPPADDING', (0, 0), (-1, -1), 5),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 5),
        ]))
        
        story.append(info_table)
        story.append(Spacer(1, 20))
        
        # DADOS DO CLIENTE
        story.append(Paragraph('Dados do cliente', secao_style))
        
        cliente_data = [
            ['Nome', orcamento.cliente],
            ['Telefone', 'Não informado', 'Email', 'Não informado'], # Não há campos de telefone/email no modelo atual
            ['CPF / CNPJ', 'Não informado'], # Não há campo de CPF/CNPJ no modelo atual
            ['Endereço', 'Não informado'] # Não há campo de endereço no modelo atual
        ]
        
        cliente_table = Table(cliente_data, colWidths=[2.5*cm, 6*cm, 2*cm, 6.5*cm])
        cliente_table.setStyle(TableStyle([
            ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
            ('FONTNAME', (2, 1), (2, 1), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 10),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('VALIGN', (0, 0), (-1, -1), 'TOP'),
            ('LEFTPADDING', (0, 0), (-1, -1), 0),
            ('RIGHTPADDING', (0, 0), (-1, -1), 5),
            ('TOPPADDING', (0, 0), (-1, -1), 3),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 3),
        ]))
        
        story.append(cliente_table)
        story.append(Spacer(1, 25))
        
        # ITENS
        story.append(Paragraph('Itens', secao_style))
        
        # Cabeçalho da tabela de itens
        itens_data = [['#', 'Nome', 'Qtd.', 'Valor', 'Subtotal']]
        
        subtotal = 0
        servicos = orcamento.servicos # Obter serviços do orçamento
        
        for i, servico in enumerate(servicos, 1):
            descricao = servico.nome
            quantidade = servico.quantidade
            valor_unitario = servico.preco_unitario
            total_item = quantidade * valor_unitario
            subtotal += total_item
            
            itens_data.append([
                str(i),
                descricao,
                f"{quantidade:.0f}" if quantidade == int(quantidade) else f"{quantidade:.2f}".replace('.', ','),
                f"R$ {valor_unitario:.2f}".replace('.', ','),
                f"R$ {total_item:.2f}".replace('.', ',')
            ])
        
        # Se não há itens, adicionar uma linha de exemplo
        if not servicos:
            itens_data.append(['1', 'Nenhum item adicionado', '0', 'R$ 0,00', 'R$ 0,00'])
        
        itens_table = Table(itens_data, colWidths=[1*cm, 9*cm, 1.5*cm, 2.5*cm, 3*cm])
        itens_table.setStyle(TableStyle([
            # Cabeçalho
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 10),
            ('ALIGN', (0, 0), (0, -1), 'CENTER'),  # #
            ('ALIGN', (1, 0), (1, -1), 'LEFT'),    # Nome
            ('ALIGN', (2, 0), (2, -1), 'CENTER'),  # Qtd
            ('ALIGN', (3, 0), (3, -1), 'RIGHT'),   # Valor
            ('ALIGN', (4, 0), (4, -1), 'RIGHT'),   # Subtotal
            
            # Dados
            ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 1), (-1, -1), 10),
            
            # Linha horizontal apenas no cabeçalho
            ('LINEBELOW', (0, 0), (-1, 0), 1, colors.black),
            
            # Padding
            ('LEFTPADDING', (0, 0), (-1, -1), 3),
            ('RIGHTPADDING', (0, 0), (-1, -1), 3),
            ('TOPPADDING', (0, 0), (-1, -1), 4),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
            ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ]))
        
        story.append(itens_table)
        story.append(Spacer(1, 20))
        
        # TOTAIS
        # O modelo Orcamento não tem campos para desconto e acréscimo diretamente
        # Vou calcular o subtotal dos serviços e usar isso como base
        # Se houver necessidade de desconto/acréscimo, precisaria de campos no modelo
        
        total_geral = subtotal # Por enquanto, total é igual ao subtotal
        
        totais_data = [
            ['Subtotal:', f"R$ {subtotal:.2f}".replace('.', ','), 'Total:', f"R$ {total_geral:.2f}".replace('.', ',')]
        ]
        
        totais_table = Table(totais_data, colWidths=[2*cm, 2.5*cm, 1.5*cm, 2*cm])
        totais_table.setStyle(TableStyle([
            ('FONTNAME', (0, 0), (-1, -1), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 10),
            ('ALIGN', (0, 0), (-1, -1), 'RIGHT'),
            ('LEFTPADDING', (0, 0), (-1, -1), 3),
            ('RIGHTPADDING', (0, 0), (-1, -1), 3),
            ('TOPPADDING', (0, 0), (-1, -1), 5),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 5),
        ]))
        
        story.append(totais_table)
        story.append(Spacer(1, 20))
        
        # OBSERVAÇÕES
        observacoes = orcamento.descricao # Usando a descrição do orçamento como observações
        if not observacoes or not observacoes.strip():
            observacoes = "Nenhuma observação informada."
        
        story.append(Paragraph('Observações', secao_style))
        story.append(Paragraph(observacoes.replace('\n', '<br/>'), normal_style))
        story.append(Spacer(1, 30))
        
        # ASSINATURAS
        assinatura_data = [
            ['Eighmen', orcamento.cliente]
        ]
        
        assinatura_table = Table(assinatura_data, colWidths=[8.5*cm, 8.5*cm])
        assinatura_table.setStyle(TableStyle([
            ('FONTNAME', (0, 0), (-1, -1), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 11),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('LINEABOVE', (0, 0), (-1, -1), 1, colors.black),
            ('LEFTPADDING', (0, 0), (-1, -1), 0),
            ('RIGHTPADDING', (0, 0), (-1, -1), 0),
            ('TOPPADDING', (0, 0), (-1, -1), 5),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 0),
        ]))
        
        story.append(assinatura_table)
        
        # Gerar PDF
        doc.build(story)
        
        # Preparar resposta
        buffer.seek(0)
        
        nome_arquivo = f"orcamento-n{orcamento.id}.pdf"
        
        return send_file(
            buffer,
            as_attachment=True,
            download_name=nome_arquivo,
            mimetype='application/pdf'
        )
        
    except Exception as e:
        print(f"Erro ao gerar PDF: {str(e)}")
        import traceback
        traceback.print_exc()
        return jsonify({'erro': 'Erro interno do servidor', 'detalhes': str(e)}), 500



