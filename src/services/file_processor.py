import os
from utils.logger import logger
from utils.database import get_db_connection
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError

def parse_line(line):
    """Extrai dados de uma linha do arquivo."""
    user_id = int(line[0:10].strip())
    name = line[10:55].strip()
    order_id = int(line[55:65].strip())
    product_id = int(line[65:75].strip())
    value = float(line[75:87].strip())
    date_str = line[87:95].strip()
    date = f"{date_str[:4]}-{date_str[4:6]}-{date_str[6:8]}"
    return user_id, name, order_id, product_id, value, date

def insert_user(session, user_id, name):
    """Insere um usuário no banco de dados."""
    logger.info(f"Inserindo usuário: {user_id}, nome: {name}")
    session.execute(
        ('INSERT OR IGNORE INTO users (user_id, name) VALUES (:user_id, :name)'),
        {"user_id": user_id, "name": name}
    )

def insert_order(session, order_id, user_id, total, date):
    """Insere um pedido no banco de dados."""
    logger.info(f"Inserindo pedido: {order_id}, usuário: {user_id}, total: {total}, data: {date}")
    session.execute(
        ('INSERT OR IGNORE INTO orders (order_id, user_id, total, date) VALUES (:order_id, :user_id, :total, :date)'),
        {"order_id": order_id, "user_id": user_id, "total": total, "date": date}
    )

def insert_product(session, product_id, order_id, value):
    """Insere um produto no banco de dados."""
    logger.info(f"Inserindo produto: {product_id}, pedido: {order_id}, valor: {value}")
    session.execute(
        ('INSERT OR IGNORE INTO products (product_id, order_id, value) VALUES (:product_id, :order_id, :value)'),
        {"product_id": product_id, "order_id": order_id, "value": value}
    )

def process_file(file_path):
    """Processa o arquivo e salva os dados no banco de dados."""
    try:
        with open(file_path, 'r') as file:
            session: Session = get_db_connection()

            for line in file:
                line = line.strip()
                logger.info(f"Processando linha: {line}")

                user_id, name, order_id, product_id, value, date = parse_line(line)

                insert_user(session, user_id, name)  
                insert_order(session, order_id, user_id, value, date)  
                insert_product(session, product_id, order_id, value)  

            session.commit()  
            logger.info(f"Dados do arquivo {file_path} salvos no banco de dados")

    except IntegrityError as e:
        logger.error(f"Erro de integridade ao processar arquivo {file_path}: {str(e)}")
        session.rollback() 
        raise
    except Exception as e:
        logger.error(f"Erro ao processar arquivo {file_path}: {str(e)}")
        raise
    finally:
        session.close()  