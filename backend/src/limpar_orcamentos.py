import os
import sqlite3

# Caminho para o banco de dados
db_path = os.path.join(os.path.dirname(__file__), 'database', 'app.db')

# Conectar ao banco
conn = sqlite3.connect(db_path)
cursor = conn.cursor()

# Apagar dados relacionados a orçamentos
try:
    cursor.execute("DELETE FROM servicos_orcamento;")
    cursor.execute("DELETE FROM orcamentos;")
    conn.commit()
    print("✅ Orçamentos e serviços de orçamentos apagados com sucesso.")
except Exception as e:
    print("❌ Erro ao apagar dados:", e)
finally:
    conn.close()
