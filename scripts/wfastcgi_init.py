"""
Script de inicialización para wfastcgi
Configura PyMySQL antes de cargar Django
"""

# CRÍTICO: Importar el parche ANTES de cualquier cosa de Django
import pymysql_patch

# Importar y retornar la aplicación WSGI de Django
from config.wsgi import application
