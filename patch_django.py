#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import os

django_mysql_base = r"C:\Users\Administrator\AppData\Local\Programs\Python\Python314\Lib\site-packages\django\db\backends\mysql\base.py"

# Código nuevo con indentación perfecta
new_import_section = '''try:
    import MySQLdb as Database
except ImportError as err:
    try:
        import pymysql
        pymysql.install_as_MySQLdb()
        import MySQLdb as Database
    except ImportError:
        raise ImproperlyConfigured(
            "Error loading MySQLdb module.\\nDid you install mysqlclient?"
        ) from err
'''

# Leer el archivo
with open(django_mysql_base, 'r', encoding='utf-8') as f:
    lines = f.readlines()

# Buscar y reemplazar
new_lines = []
i = 0
while i < len(lines):
    line = lines[i]

    # Detectar el inicio del bloque try para MySQLdb
    if line.strip() == 'try:' and i + 1 < len(lines) and 'import MySQLdb as Database' in lines[i + 1]:
        # Saltar hasta el final del except
        j = i + 1
        while j < len(lines):
            if lines[j].strip().startswith('from MySQLdb'):
                break
            j += 1

        # Insertar el nuevo código
        new_lines.append(new_import_section)
        i = j
        continue

    new_lines.append(line)
    i += 1

# Escribir
with open(django_mysql_base, 'w', encoding='utf-8', newline='\n') as f:
    f.writelines(new_lines)

print("✓ Archivo parcheado correctamente")
print(f"✓ Total de líneas: {len(new_lines)}")
