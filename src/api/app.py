import sys
import os


sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from flask import Flask
from utils.database import init_db  
from api.controllers.api_controller import order_blueprint  
from config.settings import UPLOAD_FOLDER, PROCESSED_FOLDER
from utils.logger import logger

app = Flask(__name__)


app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['PROCESSED_FOLDER'] = PROCESSED_FOLDER
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  

os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(PROCESSED_FOLDER, exist_ok=True)


app.register_blueprint(order_blueprint)

@app.route('/health', methods=['GET'])
def health_check():
    """Endpoint para verificar o status da aplicação."""
    return {"status": "healthy"}, 200

if __name__ == '__main__':
    init_db()
    logger.info("Iniciar")
    app.run(port=5000)  