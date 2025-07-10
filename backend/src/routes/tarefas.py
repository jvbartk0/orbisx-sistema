from flask import Blueprint, request, jsonify
from datetime import datetime, date
from src.models.user import db
from src.models.tarefa import Tarefa

tarefas_bp = Blueprint('tarefas', __name__)

@tarefas_bp.route('/tarefas', methods=['GET'])
def listar_tarefas():
    try:
        # Filtros opcionais
        data_inicio = request.args.get('data_inicio')
        data_fim = request.args.get('data_fim')
        tipo = request.args.get('tipo')
        concluida = request.args.get('concluida')
        
        query = Tarefa.query
        
        # Aplicar filtros
        if data_inicio:
            try:
                data_inicio_obj = datetime.strptime(data_inicio, '%Y-%m-%d').date()
                query = query.filter(Tarefa.data >= data_inicio_obj)
            except ValueError:
                return jsonify({'error': 'Formato de data inválido para data_inicio'}), 400
        
        if data_fim:
            try:
                data_fim_obj = datetime.strptime(data_fim, '%Y-%m-%d').date()
                query = query.filter(Tarefa.data <= data_fim_obj)
            except ValueError:
                return jsonify({'error': 'Formato de data inválido para data_fim'}), 400
        
        if tipo:
            query = query.filter(Tarefa.tipo == tipo)
        
        if concluida is not None:
            concluida_bool = concluida.lower() == 'true'
            query = query.filter(Tarefa.concluida == concluida_bool)
        
        tarefas = query.order_by(Tarefa.data.asc(), Tarefa.horario.asc()).all()
        
        return jsonify({
            'tarefas': [tarefa.to_dict() for tarefa in tarefas]
        }), 200
        
    except Exception as e:
        return jsonify({'error': 'Erro interno do servidor'}), 500

@tarefas_bp.route('/tarefas', methods=['POST'])
def criar_tarefa():
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({'error': 'Dados não fornecidos'}), 400
        
        # Validações obrigatórias
        titulo = data.get('titulo', '').strip()
        tipo = data.get('tipo', '').strip()
        data_tarefa = data.get('data', '').strip()
        horario = data.get('horario', '').strip()
        cliente = data.get('cliente', '').strip()
        local = data.get('local', '').strip()
        descricao = data.get('descricao', '').strip()
        
        if not titulo:
            return jsonify({'error': 'Título é obrigatório'}), 400
        
        if not tipo or tipo not in ['captacao', 'edicao', 'reuniao']:
            return jsonify({'error': 'Tipo deve ser "captacao", "edicao" ou "reuniao"'}), 400
        
        if not data_tarefa:
            return jsonify({'error': 'Data é obrigatória'}), 400
        
        # Converter data
        try:
            data_obj = datetime.strptime(data_tarefa, '%Y-%m-%d').date()
        except ValueError:
            return jsonify({'error': 'Formato de data inválido'}), 400
        
        # Converter horário se fornecido
        horario_obj = None
        if horario:
            try:
                horario_obj = datetime.strptime(horario, '%H:%M').time()
            except ValueError:
                return jsonify({'error': 'Formato de horário inválido (use HH:MM)'}), 400
        
        # Criar nova tarefa
        nova_tarefa = Tarefa(
            titulo=titulo,
            tipo=tipo,
            data=data_obj,
            horario=horario_obj,
            cliente=cliente,
            local=local,
            descricao=descricao
        )
        
        db.session.add(nova_tarefa)
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': 'Tarefa criada com sucesso',
            'tarefa': nova_tarefa.to_dict()
        }), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': 'Erro interno do servidor'}), 500

@tarefas_bp.route('/tarefas/<int:tarefa_id>/concluir', methods=['PUT'])
def marcar_concluida(tarefa_id):
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({'error': 'Dados não fornecidos'}), 400
        
        concluida = data.get('concluida', False)
        
        tarefa = Tarefa.query.get(tarefa_id)
        
        if not tarefa:
            return jsonify({'error': 'Tarefa não encontrada'}), 404
        
        tarefa.concluida = bool(concluida)
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': 'Status da tarefa atualizado com sucesso',
            'tarefa': tarefa.to_dict()
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': 'Erro interno do servidor'}), 500

@tarefas_bp.route('/tarefas/<int:tarefa_id>', methods=['DELETE'])
def deletar_tarefa(tarefa_id):
    try:
        tarefa = Tarefa.query.get(tarefa_id)
        
        if not tarefa:
            return jsonify({'error': 'Tarefa não encontrada'}), 404
        
        db.session.delete(tarefa)
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': 'Tarefa removida com sucesso'
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': 'Erro interno do servidor'}), 500

@tarefas_bp.route('/tarefas/calendario/<int:ano>/<int:mes>', methods=['GET'])
def calendario_mes(ano, mes):
    try:
        # Validar ano e mês
        if mes < 1 or mes > 12:
            return jsonify({'error': 'Mês inválido'}), 400
        
        if ano < 2000 or ano > 2100:
            return jsonify({'error': 'Ano inválido'}), 400
        
        # Buscar tarefas do mês
        data_inicio = date(ano, mes, 1)
        
        # Calcular último dia do mês
        if mes == 12:
            data_fim = date(ano + 1, 1, 1)
        else:
            data_fim = date(ano, mes + 1, 1)
        
        tarefas = Tarefa.query.filter(
            Tarefa.data >= data_inicio,
            Tarefa.data < data_fim
        ).all()
        
        # Agrupar tarefas por dia
        calendario = {}
        for tarefa in tarefas:
            dia = tarefa.data.day
            if dia not in calendario:
                calendario[dia] = []
            calendario[dia].append(tarefa.to_dict())
        
        return jsonify({
            'ano': ano,
            'mes': mes,
            'calendario': calendario
        }), 200
        
    except Exception as e:
        return jsonify({'error': 'Erro interno do servidor'}), 500

@tarefas_bp.route('/tarefas/estatisticas', methods=['GET'])
def estatisticas_tarefas():
    try:
        # Filtros opcionais
        data_inicio = request.args.get('data_inicio')
        data_fim = request.args.get('data_fim')
        
        query = Tarefa.query
        
        # Aplicar filtros de data se fornecidos
        if data_inicio:
            try:
                data_inicio_obj = datetime.strptime(data_inicio, '%Y-%m-%d').date()
                query = query.filter(Tarefa.data >= data_inicio_obj)
            except ValueError:
                return jsonify({'error': 'Formato de data inválido para data_inicio'}), 400
        
        if data_fim:
            try:
                data_fim_obj = datetime.strptime(data_fim, '%Y-%m-%d').date()
                query = query.filter(Tarefa.data <= data_fim_obj)
            except ValueError:
                return jsonify({'error': 'Formato de data inválido para data_fim'}), 400
        
        tarefas = query.all()
        
        # Calcular estatísticas
        total_tarefas = len(tarefas)
        concluidas = len([t for t in tarefas if t.concluida])
        pendentes = total_tarefas - concluidas
        
        # Agrupar por categoria
        por_categoria = {
            'captacao': len([t for t in tarefas if t.tipo == 'captacao']),
            'edicao': len([t for t in tarefas if t.tipo == 'edicao']),
            'reuniao': len([t for t in tarefas if t.tipo == 'reuniao'])
        }
        
        # Calcular taxa de conclusão
        taxa_conclusao = (concluidas / total_tarefas * 100) if total_tarefas > 0 else 0
        
        return jsonify({
            'total_tarefas': total_tarefas,
            'concluidas': concluidas,
            'pendentes': pendentes,
            'taxa_conclusao': round(taxa_conclusao, 1),
            'por_categoria': por_categoria
        }), 200
        
    except Exception as e:
        return jsonify({'error': 'Erro interno do servidor'}), 500

