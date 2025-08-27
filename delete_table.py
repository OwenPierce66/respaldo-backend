import sqlite3

# Ruta a tu base de datos SQLite
db_path = 'db.sqlite3'  # Asegúrate de que esta ruta sea correcta

# Conexión a la base de datos
conn = sqlite3.connect(db_path)
cursor = conn.cursor()

# Eliminar la tabla conflictiva
cursor.execute("DROP TABLE IF EXISTS api_sharedtask")

# Confirmar los cambios
conn.commit()

# Cerrar la conexión
conn.close()

print("Tabla api_sharedtask eliminada.")
