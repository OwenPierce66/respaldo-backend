import sqlite3

conn = sqlite3.connect('db.sqlite3')
cursor = conn.cursor()

# Encontrar y eliminar registros huérfanos
cursor.execute("""
    DELETE FROM api_newpeticioncomment
    WHERE created_by_id NOT IN (SELECT id FROM auth_user)
""")

# Confirmar los cambios
conn.commit()

# Verificar integridad referencial
cursor.execute("PRAGMA foreign_key_check")
print(cursor.fetchall())

# Cerrar la conexión
conn.close()
