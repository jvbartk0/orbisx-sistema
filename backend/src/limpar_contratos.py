import os
import sqlite3

# Caminho para o banco de dados
db_path = os.path.join(os.path.dirname(__file__), 'database', 'app.db')

# Conectar ao banco
conn = sqlite3.connect(db_path)
cursor = conn.cursor()

# Apagar contratos
try:
    cursor.execute("DELETE FROM contratos;")
    conn.commit()
    print("✅ Contratos apagados com sucesso.")
except Exception as e:
    print("❌ Erro ao apagar dados:", e)
finally:
    conn.close()
