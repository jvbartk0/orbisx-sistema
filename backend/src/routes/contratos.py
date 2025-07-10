from flask import Blueprint, request, jsonify, send_file
from datetime import datetime
from werkzeug.utils import secure_filename
import os
from src.models.user import db
from src.models.contrato import Contrato

contratos_bp = Blueprint('contratos', __name__)

# Configurações de upload
UPLOAD_FOLDER = 'uploads/contratos'
ALLOWED_EXTENSIONS = {'pdf'}
MAX_FILE_SIZE = 16 * 1024 * 1024  # 16MB

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def create_upload_folder():
    upload_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), UPLOAD_FOLDER)
    if not os.path.exists(upload_path):
        os.makedirs(upload_path)
    return upload_path

@contratos_bp.route('/contratos', methods=['GET'])
def listar_contratos():
    try:
        # Filtros opcionais
        cliente = request.args.get('cliente')
        data_inicio = request.args.get('data_inicio')
        data_fim = request.args.get('data_fim')
        
        query = Contrato.query
        
        # Aplicar filtros
        if cliente:
            query = query.filter(Contrato.cliente.ilike(f'%{cliente}%'))
        
        if data_inicio:
            try:
                data_inicio_obj = datetime.strptime(data_inicio, '%Y-%m-%d').date()
                query = query.filter(Contrato.data_inicio >= data_inicio_obj)
            except ValueError:
                return jsonify({'error': 'Formato de data inválido para data_inicio'}), 400
        
        if data_fim:
            try:
                data_fim_obj = datetime.strptime(data_fim, '%Y-%m-%d').date()
                query = query.filter(Contrato.data_fim <= data_fim_obj)
            except ValueError:
                return jsonify({'error': 'Formato de data inválido para data_fim'}), 400
        
        contratos = query.order_by(Contrato.data_upload.desc()).all()
        
        return jsonify({
            'contratos': [contrato.to_dict() for contrato in contratos]
        }), 200
        
    except Exception as e:
        return jsonify({'error': 'Erro interno do servidor'}), 500

@contratos_bp.route('/contratos', methods=['POST'])
def criar_contrato():
    try:
        # Verificar se há arquivo no request
        if 'arquivo' not in request.files:
            return jsonify({'error': 'Arquivo PDF é obrigatório'}), 400
        
        arquivo = request.files['arquivo']
        
        if arquivo.filename == '':
            return jsonify({'error': 'Nenhum arquivo selecionado'}), 400
        
        if not allowed_file(arquivo.filename):
            return jsonify({'error': 'Apenas arquivos PDF são permitidos'}), 400
        
        # Verificar tamanho do arquivo
        arquivo.seek(0, os.SEEK_END)
        file_size = arquivo.tell()
        arquivo.seek(0)
        
        if file_size > MAX_FILE_SIZE:
            return jsonify({'error': 'Arquivo muito grande. Máximo 16MB'}), 400
        
        # Obter dados do formulário
        titulo = request.form.get('titulo', '').strip()
        cliente = request.form.get('cliente', '').strip()
        valor = request.form.get('valor')
        data_inicio = request.form.get('data_inicio', '').strip()
        data_fim = request.form.get('data_fim', '').strip()
        observacoes = request.form.get('observacoes', '').strip()
        
        # Validações obrigatórias
        if not titulo:
            return jsonify({'error': 'Título é obrigatório'}), 400
        
        if not cliente:
            return jsonify({'error': 'Cliente é obrigatório'}), 400
        
        if not valor or float(valor) <= 0:
            return jsonify({'error': 'Valor deve ser maior que zero'}), 400
        
        if not data_inicio:
            return jsonify({'error': 'Data de início é obrigatória'}), 400
        
        if not data_fim:
            return jsonify({'error': 'Data de fim é obrigatória'}), 400
        
        # Converter datas
        try:
            data_inicio_obj = datetime.strptime(data_inicio, '%Y-%m-%d').date()
            data_fim_obj = datetime.strptime(data_fim, '%Y-%m-%d').date()
        except ValueError:
            return jsonify({'error': 'Formato de data inválido'}), 400
        
        if data_fim_obj <= data_inicio_obj:
            return jsonify({'error': 'Data de fim deve ser posterior à data de início'}), 400
        
        # Salvar arquivo
        upload_path = create_upload_folder()
        filename = secure_filename(arquivo.filename)
        
        # Gerar nome único para evitar conflitos
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        nome_arquivo = f"{timestamp}_{filename}"
        caminho_completo = os.path.join(upload_path, nome_arquivo)
        
        arquivo.save(caminho_completo)
        
        # Criar novo contrato
        novo_contrato = Contrato(
            titulo=titulo,
            cliente=cliente,
            valor=float(valor),
            data_inicio=data_inicio_obj,
            data_fim=data_fim_obj,
            observacoes=observacoes,
            nome_arquivo=filename,
            caminho_arquivo=caminho_completo
        )
        
        db.session.add(novo_contrato)
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': 'Contrato criado com sucesso',
            'contrato': novo_contrato.to_dict()
        }), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': 'Erro interno do servidor'}), 500

@contratos_bp.route('/contratos/<int:contrato_id>/download', methods=['GET'])
def download_contrato(contrato_id):
    try:
        contrato = Contrato.query.get(contrato_id)
        
        if not contrato:
            return jsonify({'error': 'Contrato não encontrado'}), 404
        
        if not contrato.caminho_arquivo or not os.path.exists(contrato.caminho_arquivo):
            return jsonify({'error': 'Arquivo não encontrado'}), 404
        
        return send_file(
            contrato.caminho_arquivo,
            as_attachment=True,
            download_name=contrato.nome_arquivo,
            mimetype='application/pdf'
        )
        
    except Exception as e:
        return jsonify({'error': 'Erro interno do servidor'}), 500

@contratos_bp.route('/contratos/<int:contrato_id>/view', methods=['GET'])
def visualizar_contrato(contrato_id):
    try:
        contrato = Contrato.query.get(contrato_id)
        
        if not contrato:
            return jsonify({'error': 'Contrato não encontrado'}), 404
        
        if not contrato.caminho_arquivo or not os.path.exists(contrato.caminho_arquivo):
            return jsonify({'error': 'Arquivo não encontrado'}), 404
        
        return send_file(
            contrato.caminho_arquivo,
            mimetype='application/pdf'
        )
        
    except Exception as e:
        return jsonify({'error': 'Erro interno do servidor'}), 500

@contratos_bp.route('/contratos/clientes', methods=['GET'])
def listar_clientes_contratos():
    try:
        # Buscar clientes únicos
        clientes = db.session.query(Contrato.cliente).distinct().all()
        clientes_list = [cliente[0] for cliente in clientes if cliente[0]]
        
        return jsonify({
            'clientes': sorted(clientes_list)
        }), 200
        
    except Exception as e:
        return jsonify({'error': 'Erro interno do servidor'}), 500

