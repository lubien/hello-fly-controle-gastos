from flask import Flask, render_template
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_cors import CORS
from app.config import config

db = SQLAlchemy()
migrate = Migrate()


def create_app(config_name='development'):
    """Factory de criação da aplicação Flask"""
    app = Flask(__name__)
    app.config.from_object(config[config_name])
    
    # Inicializa extensões
    db.init_app(app)
    migrate.init_app(app, db)
    CORS(app)
    
    # Registra blueprints
    from app.routes.gastos import gastos_bp
    from app.routes.categorias import categorias_bp
    from app.routes.relatorios import relatorios_bp
    
    app.register_blueprint(gastos_bp, url_prefix='/api/gastos')
    app.register_blueprint(categorias_bp, url_prefix='/api/categorias')
    app.register_blueprint(relatorios_bp, url_prefix='/api/relatorios')
    
    # Rota de health check
    @app.route('/health')
    def health():
        return {'status': 'healthy', 'message': 'Sistema de Controle de Gastos funcionando!'}
    
    # Rota principal - Frontend
    @app.route('/')
    def index():
        return render_template('index.html')
    
    # Rota de API info
    @app.route('/api')
    def api_info():
        return {
            'app': 'Sistema de Controle de Gastos',
            'version': '1.0.0',
            'endpoints': {
                'gastos': '/api/gastos',
                'categorias': '/api/categorias',
                'relatorios': '/api/relatorios',
                'health': '/health'
            }
        }
    
    return app
