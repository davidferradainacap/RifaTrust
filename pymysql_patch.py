"""
Parche dinámico para PyMySQL
Se importa ANTES que Django para reemplazar MySQLdb
"""
import sys
import pymysql

# Instalar PyMySQL como MySQLdb
pymysql.install_as_MySQLdb()

# Monkey-patch para asegurar que MySQLdb apunte a pymysql
sys.modules['MySQLdb'] = pymysql
sys.modules['_mysql'] = pymysql

print("[PYMYSQL_PATCH] PyMySQL instalado como MySQLdb", flush=True)
