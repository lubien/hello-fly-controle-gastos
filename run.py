import os
import time
from app import create_app, db
from app.models import Categoria, Gasto, OrcamentoMensal

app = create_app(os.getenv('FLASK_ENV', 'development'))


def wait_for_db():
    """Aguarda o banco de dados estar disponível"""
    max_retries = 30
    retry_count = 0
    
    while retry_count < max_retries:
        try:
            with app.app_context():
                db.engine.connect()
                print("✅ Conexão com banco de dados estabelecida!")
                return True
        except Exception as e:
            retry_count += 1
            print(f"⏳ Aguardando banco de dados... ({retry_count}/{max_retries})")
            time.sleep(2)
    
    print("❌ Não foi possível conectar ao banco de dados")
    return False


def init_db():
    """Inicializa o banco de dados"""
    with app.app_context():
        db.create_all()
        print("✅ Tabelas criadas com sucesso!")


if __name__ == '__main__':
    print("🚀 Iniciando Sistema de Controle de Gastos...")
    
    if wait_for_db():
        init_db()
        print("🌐 Servidor rodando em http://localhost:5000")
        app.run(host='0.0.0.0', port=5000, debug=True)
