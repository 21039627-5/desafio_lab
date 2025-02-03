import os
from flask import Blueprint, request, jsonify
from services.file_processor import process_file
from config.settings import UPLOAD_FOLDER
from utils.logger import logger
from utils.database import get_db_connection, init_db
from werkzeug.utils import secure_filename


order_blueprint = Blueprint('order', __name__)


@order_blueprint.route('/health', methods=['GET'])
def health_check():
    """Endpoint para verificar o status da aplicação."""
    try:
        if not os.path.exists(UPLOAD_FOLDER):
            return jsonify({"status": "error", "message": "Pasta de upload não encontrada"}), 500

        return jsonify({"status": "healthy"}), 200
    except Exception as e:
        logger.error(f"Erro no health check: {str(e)}")
        return jsonify({"status": "error", "message": str(e)}), 500

@order_blueprint.route('/upload', methods=['POST'])
def upload_file():
    """Endpoint para upload de arquivos .txt."""
    if 'file' not in request.files:
        logger.error("Nenhum arquivo enviado")
        return jsonify({"error": "No file part"}), 400

    files = request.files.getlist('file')  
    if not files:
        logger.error("Nenhum arquivo selecionado")
        return jsonify({"error": "No selected files"}), 400

    try:
        os.makedirs(UPLOAD_FOLDER, exist_ok=True)  
        for file in files:
            if file.filename == '':
                logger.error("Nome do arquivo vazio")
                continue  

            if not file.filename.endswith('.txt'):
                logger.error(f"Arquivo {file.filename} não é do tipo .txt")
                continue  

            filename = secure_filename(file.filename)
            file_path = os.path.join(UPLOAD_FOLDER, filename)

            file.save(file_path)  

            logger.info(f"Recebido arquivo: {filename}, tamanho: {os.path.getsize(file_path)} bytes")
            
            process_file(file_path)  

        logger.info("Todos os arquivos processados com sucesso")
        return jsonify({"message": "Arquivos processados com sucesso"}), 200
    except Exception as e:
        logger.error(f"Erro ao processar arquivos: {str(e)}")
        return jsonify({"error": "Erro ao processar arquivos"}), 500

@order_blueprint.route('/orders', methods=['GET'])
def get_orders():
    """Endpoint para consultar pedidos."""
    order_id = request.args.get('order_id')
    start_date = request.args.get('start_date')
    end_date = request.args.get('end_date')

    logger.info(f"Consultando pedidos com parâmetros: order_id={order_id}, start_date={start_date}, end_date={end_date}")

    try:
        session = get_db_connection()  
        query = '''
            SELECT u.user_id, u.name, o.order_id, o.total, o.date, p.product_id, p.value
            FROM users u
            JOIN orders o ON u.user_id = o.user_id
            LEFT JOIN products p ON o.order_id = p.order_id  -- Usar LEFT JOIN para incluir todos os pedidos
        '''
        conditions = []
        params = {}

        if order_id:
            conditions.append("o.order_id = :order_id")
            params['order_id'] = order_id

        if start_date and end_date:
            conditions.append("o.date BETWEEN :start_date AND :end_date")
            params['start_date'] = start_date
            params['end_date'] = end_date

        if conditions:
            query += " WHERE " + " AND ".join(conditions)

        logger.info(f"Executando consulta: {query} com parâmetros {params}")

        result = session.execute((query), params)
        rows = result.fetchall()

        logger.info(f"Consulta retornou {len(rows)} resultados.")

        users = {}
        for row in rows:
            user_id, name, order_id, total, date, product_id, value = row

            if user_id not in users:
                users[user_id] = {"user_id": user_id, "name": name, "orders": []}

            
            order = next((order for order in users[user_id]["orders"] if order["order_id"] == order_id), None)
            if not order:
                
                order = {
                    "order_id": order_id,
                    "total": total,
                    "date": date,
                    "products": []  
                }
                users[user_id]["orders"].append(order)

            
            if product_id is not None:
                order["products"].append({"product_id": product_id, "value": value})

        session.close()  

        logger.info("Dados consultados com sucesso")
        return jsonify(list(users.values())), 200  
    except Exception as e:
        logger.error(f"Erro ao consultar pedidos: {str(e)}")
        return jsonify({"error": "Erro ao consultar pedidos"}), 500