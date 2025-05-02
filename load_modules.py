import re
from db_sqlite import SessionLocal, create_tables, EnglishModule

def load_modules_from_file(file_path):
    modules_data = []
    
    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            for line in file:
                line = line.strip()
                if not line:
                    continue
                
                # Extraer los componentes de la tupla utilizando expresiones regulares
                match = re.match(r"\('([^']+)', '([^']+)', '([^']+)'\)", line)
                if match:
                    level, title, description = match.groups()
                    modules_data.append((level, title, description))
                else:
                    print(f"No se pudo parsear la línea: {line}")
    except Exception as e:
        print(f"Error al leer el archivo: {e}")
        return False
    
    if not modules_data:
        print("No se encontraron módulos para cargar")
        return False
    
    # Insertar en la base de datos
    db = SessionLocal()
    try:
        # Verificar si ya hay módulos en la base de datos
        existing_modules = db.query(EnglishModule).count()
        if existing_modules > 0:
            print(f"Ya hay {existing_modules} módulos en la base de datos. Omitiendo carga.")
            return True
        
        # Cargar los módulos
        for level, title, description in modules_data:
            EnglishModule.create(db, level, title, description)
        
        print(f"Se cargaron {len(modules_data)} módulos exitosamente.")
        return True
    except Exception as e:
        print(f"Error al cargar los módulos a la base de datos: {e}")
        return False
    finally:
        db.close()

if __name__ == "__main__":
    # Asegurar que las tablas estén creadas
    create_tables()
    
    # Cargar los módulos
    success = load_modules_from_file("Modulos.txt")
    if success:
        print("Proceso completado con éxito.")
    else:
        print("El proceso falló.") 