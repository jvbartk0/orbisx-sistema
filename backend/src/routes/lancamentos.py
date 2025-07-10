from flask import Blueprint, request, jsonify
from datetime import datetime, date
from src.models.user import db
from src.models.lancamento import Lancamento

lancamentos_bp = Blueprint('lancamentos', __name__)

@lancamentos_bp.route('/lancamentos', methods=['GET'])
def listar_lancamentos():
    try:
        # Filtros opcionais
        data_inicio = request.args.get('data_inicio')
        data_fim = request.args.get('data_fim')
        
        query = Lancamento.query
        
        # Aplicar filtros de data se fornecidos
        if data_inicio:
            try:
                data_inicio_obj = datetime.strptime(data_inicio, '%Y-%m-%d').date()
                query = query.filter(Lancamento.data >= data_inicio_obj)
            except ValueError:
                return jsonify({'error': 'Formato de data inválido para data_inicio'}), 400
        
        if data_fim:
            try:
                data_fim_obj = datetime.strptime(data_fim, '%Y-%m-%d').date()
                query = query.filter(Lancamento.data <= data_fim_obj)
            except ValueError:
                return jsonify({'error': 'Formato de data inválido para data_fim'}), 400
        
        lancamentos = query.order_by(Lancamento.data.desc()).all()
        
        return jsonify({
            'lancamentos': [lancamento.to_dict() for lancamento in lancamentos]
        }), 200
        
    except Exception as e:
        return jsonify({'error': 'Erro interno do servidor'}), 500

@lancamentos_bp.route('/lancamentos', methods=['POST'])
def criar_lancamento():
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({'error': 'Dados não fornecidos'}), 400
        
        # Validações obrigatórias
        tipo = data.get('tipo', '').strip()
        valor = data.get('valor')
        data_lancamento = data.get('data', '').strip()
        categoria = data.get('categoria', '').strip()
        descricao = data.get('descricao', '').strip()
        
        if not tipo or tipo not in ['entrada', 'saida']:
            return jsonify({'error': 'Tipo deve ser "entrada" ou "saida"'}), 400
        
        if not valor or valor <= 0:
            return jsonify({'error': 'Valor deve ser maior que zero'}), 400
        
        if not data_lancamento:
            return jsonify({'error': 'Data é obrigatória'}), 400
        
        if not categoria:
            return jsonify({'error': 'Categoria é obrigatória'}), 400
        
        # Converter data
        try:
            data_obj = datetime.strptime(data_lancamento, '%Y-%m-%d').date()
        except ValueError:
            return jsonify({'error': 'Formato de data inválido'}), 400
        
        # Criar novo lançamento
        novo_lancamento = Lancamento(
            tipo=tipo,
            valor=float(valor),
            data=data_obj,
            categoria=categoria,
            descricao=descricao
        )
        
        db.session.add(novo_lancamento)
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': 'Lançamento criado com sucesso',
            'lancamento': novo_lancamento.to_dict()
        }), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': 'Erro interno do servidor'}), 500

@lancamentos_bp.route('/lancamentos/<int:lancamento_id>', methods=['DELETE'])
def deletar_lancamento(lancamento_id):
    try:
        lancamento = Lancamento.query.get(lancamento_id)
        
        if not lancamento:
            return jsonify({'error': 'Lançamento não encontrado'}), 404
        
        db.session.delete(lancamento)
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': 'Lançamento removido com sucesso'
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': 'Erro interno do servidor'}), 500

@lancamentos_bp.route('/lancamentos/resumo', methods=['GET'])
def resumo_financeiro():
    try:
        # Filtros opcionais
        data_inicio = request.args.get('data_inicio')
        data_fim = request.args.get('data_fim')
        
        query = Lancamento.query
        
        # Aplicar filtros de data se fornecidos
        if data_inicio:
            try:
                data_inicio_obj = datetime.strptime(data_inicio, '%Y-%m-%d').date()
                query = query.filter(Lancamento.data >= data_inicio_obj)
            except ValueError:
                return jsonify({'error': 'Formato de data inválido para data_inicio'}), 400
        
        if data_fim:
            try:
                data_fim_obj = datetime.strptime(data_fim, '%Y-%m-%d').date()
                query = query.filter(Lancamento.data <= data_fim_obj)
            except ValueError:
                return jsonify({'error': 'Formato de data inválido para data_fim'}), 400
        
        lancamentos = query.all()
        
        # Calcular totais
        total_entradas = sum(l.valor for l in lancamentos if l.tipo == 'entrada')
        total_saidas = sum(l.valor for l in lancamentos if l.tipo == 'saida')
        total_caixa = total_entradas - total_saidas
        
        # Agrupar por categoria
        categorias = {}
        for lancamento in lancamentos:
            if lancamento.categoria not in categorias:
                categorias[lancamento.categoria] = {'entrada': 0, 'saida': 0}
            categorias[lancamento.categoria][lancamento.tipo] += lancamento.valor
        
        return jsonify({
            'total_entradas': total_entradas,
            'total_saidas': total_saidas,
            'total_caixa': total_caixa,
            'categorias': categorias
        }), 200
        
    except Exception as e:
        return jsonify({'error': 'Erro interno do servidor'}), 500

