import sqlite3
import os
import shutil
from pathlib import Path

def migrar_datos():
    print("=== MIGRACIÓN DE DATOS ===")
    
    # Rutas
    dir_actual = Path(__file__).parent
    db_vieja = dir_actual / 'catastro_propiedades.db'
    dir_nuevo = Path.home() / '.catastro_propiedades'
    db_nueva = dir_nuevo / 'catastro_propiedades.db'
    
    print(f"Origen: {db_vieja}")
    print(f"Destino: {db_nueva}")
    print("-" * 50)
    
    # Verificar si existe la base de datos antigua
    if not db_vieja.exists():
        print("[ERROR] No se encontró la base de datos antigua en la ubicación esperada.")
        return
    
    # Crear directorio si no existe
    dir_nuevo.mkdir(parents=True, exist_ok=True)
    
    try:
        # Si ya existe una base de datos nueva, hacer copia de seguridad
        if db_nueva.exists():
            backup_path = dir_nuevo / 'catastro_propiedades.backup.db'
            shutil.copy2(db_nueva, backup_path)
            print(f"[INFO] Se creó una copia de seguridad en: {backup_path}")
        
        print("[INFO] Copiando la base de datos...")
        # Copiar la base de datos
        shutil.copy2(db_vieja, db_nueva)
        print("[OK] Datos migrados exitosamente")
        
        # Verificar la integridad de los datos
        try:
            print("\nVerificando datos migrados...")
            conn = sqlite3.connect(db_nueva)
            cursor = conn.cursor()
            
            # Contar propiedades
            cursor.execute("SELECT COUNT(*) FROM propiedades")
            num_propiedades = cursor.fetchone()[0]
            
            # Contar fotos
            cursor.execute("SELECT COUNT(*) FROM fotos")
            num_fotos = cursor.fetchone()[0]
            
            print("\n=== ESTADÍSTICAS DE LA MIGRACIÓN ===")
            print(f"- Propiedades migradas: {num_propiedades}")
            print(f"- Fotos migradas: {num_fotos}")
            
        except sqlite3.Error as e:
            print(f"[ADVERTENCIA] Error al verificar los datos: {e}")
        finally:
            if 'conn' in locals():
                conn.close()
                
    except Exception as e:
        print(f"[ERROR] Durante la migración: {e}")

if __name__ == "__main__":
    print("=== MIGRADOR DE BASE DE DATOS ===")
    print("Iniciando migración automática...\n")
    
    try:
        migrar_datos()
        print("\n[COMPLETADO] La migración ha finalizado.")
    except Exception as e:
        print(f"\n[ERROR] Ocurrió un error: {e}")
    
    print("\nEste mensaje se cerrará automáticamente en 10 segundos...")
    import time
    time.sleep(10)
