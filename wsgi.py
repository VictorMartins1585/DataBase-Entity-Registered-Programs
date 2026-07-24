from app import app
from waitress import serve

if __name__ == '__main__':
    # Roda na porta 5000 ou na porta padrão da rede interna
    serve(app, host='0.0.0.0', port=5000)