import json
import logging
import psycopg2
from psycopg2 import pool

logger = logging.getLogger("init")


# Функция инициализации расписания
def init_schedule(path: str):
    try:
        with open(path, "r", encoding="utf-8") as read_file:
            schedules = json.load(read_file)
            logger.info("Successfully Initialized Class Schedule")
            return schedules
    except FileNotFoundError:
        logger.critical(f'File "{path}" not found')
        exit(2)


def init_connections_pool(**kwargs):
    try:
        connections = psycopg2.pool.ThreadedConnectionPool(2, 10, **kwargs)
        logger.info("Successful database connection pooling")
        return connections
    except (Exception, psycopg2.DatabaseError) as error:
        logger.critical(f"Error connecting to PostgreSQL {error}")
        exit(2)


def init_users_group(pool_connections: psycopg2.pool):
    try:
        connection = pool_connections.getconn()

        users_group = {}

        cursor = connection.cursor()
        cursor.execute("SELECT * FROM group_users")
        records = cursor.fetchall()

        for row in records:
            users_group[row[0]] = str(row[1]).strip()

        cursor.close()
        pool_connections.putconn(connection)
        logger.info("Successful initialization of user group number information")
        return users_group

    except (Exception, psycopg2.DatabaseError) as error:
        logger.critical(f"Error connecting to PostgreSQL {error}")
        exit(2)


def init_user_states(pool_connections: psycopg2.pool):
    try:
        connection = pool_connections.getconn()
        cursor = connection.cursor()

        cursor.execute("SELECT * FROM states")
        user_ids = cursor.fetchall()

        cursor.close()
        pool_connections.putconn(connection)

        logger.info("Successfully getting current user states")

        return {i[0]: None for i in user_ids}

    except (Exception, psycopg2.DatabaseError) as error:
        logger.critical(f"Error connecting to PostgreSQL {error}")
        exit(2)
