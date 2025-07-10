from flask import Blueprint, request, jsonify, session

auth_bp = Blueprint('auth', __name__)

# Credenciais fixas conforme especificado
USUARIO_FIXO = 'eighmen'
SENHA_FIXA = 'Eighmen8'

@auth_bp.route('/login', methods=['POST'])
def login():
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({'error': 'Dados não fornecidos'}), 400
        
        usuario = data.get('usuario', '').strip()
        senha = data.get('senha', '').strip()
        
        # Validação de campos vazios
        if not usuario or not senha:
            return jsonify({'error': 'Usuário e senha são obrigatórios'}), 400
        
        # Verificação das credenciais fixas
        if usuario == USUARIO_FIXO and senha == SENHA_FIXA:
            session['authenticated'] = True
            session['usuario'] = usuario
            return jsonify({
                'success': True,
                'message': 'Login realizado com sucesso',
                'usuario': usuario
            }), 200
        else:
            return jsonify({'error': 'Credenciais inválidas'}), 401
            
    except Exception as e:
        return jsonify({'error': 'Erro interno do servidor'}), 500

@auth_bp.route('/logout', methods=['POST'])
def logout():
    try:
        session.clear()
        return jsonify({'success': True, 'message': 'Logout realizado com sucesso'}), 200
    except Exception as e:
        return jsonify({'error': 'Erro interno do servidor'}), 500

@auth_bp.route('/check-auth', methods=['GET'])
def check_auth():
    try:
        if session.get('authenticated'):
            return jsonify({
                'authenticated': True,
                'usuario': session.get('usuario')
            }), 200
        else:
            return jsonify({'authenticated': False}), 200
    except Exception as e:
        return jsonify({'error': 'Erro interno do servidor'}), 500

