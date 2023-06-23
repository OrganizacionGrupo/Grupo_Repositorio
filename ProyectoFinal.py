import sqlite3
import os

class LeyesDB:
    def __init__(self, nombre_db):
        self.conn = sqlite3.connect(nombre_db)
        self.crear_tablas()

    def crear_tablas(self):
        query_jurisdiccion = """
        CREATE TABLE IF NOT EXISTS Jurisdiccion (
            ID TEXT PRIMARY KEY,
            Nombre TEXT NOT NULL
        )
        """
        query_normativa = """
        CREATE TABLE IF NOT EXISTS Normativa (
            Nro_Registro INTEGER PRIMARY KEY AUTOINCREMENT,
            Tipo_Normativa TEXT NOT NULL,
            Nro_Normativa TEXT NOT NULL,
            Fecha TEXT NOT NULL,
            Descripcion TEXT NOT NULL,
            Categoria TEXT NOT NULL,
            Organo_Legislativo TEXT NOT NULL,
            Jurisdiccion_ID TEXT NOT NULL,
            FOREIGN KEY (Jurisdiccion_ID) REFERENCES Jurisdiccion(ID)
        )
        """
        query_palabra_clave = """
        CREATE TABLE IF NOT EXISTS PalabraClave (
            ID INTEGER PRIMARY KEY AUTOINCREMENT,
            Palabra TEXT NOT NULL,
            Nro_Registro INTEGER NOT NULL,
            FOREIGN KEY (Nro_Registro) REFERENCES Normativa(Nro_Registro)
        )
        """
        self.conn.execute(query_jurisdiccion)
        self.conn.execute(query_normativa)
        self.conn.execute(query_palabra_clave)
        self.conn.commit()

        self.insertar_jurisdiccion("1", "Nacional")
        self.insertar_jurisdiccion("2", "Provincial")

    def insertar_jurisdiccion(self, id_jurisdiccion, nombre_jurisdiccion):
        query = "INSERT OR IGNORE INTO Jurisdiccion (ID, Nombre) VALUES (?, ?)"
        self.conn.execute(query, (id_jurisdiccion, nombre_jurisdiccion))
        self.conn.commit()

    def obtener_nombre_jurisdiccion(self, id_jurisdiccion):
        query = "SELECT Nombre FROM Jurisdiccion WHERE ID = ?"
        cursor = self.conn.execute(query, (id_jurisdiccion,))
        resultado = cursor.fetchone()
        if resultado:
            return resultado[0]
        return None

    def insertar_normativa(self, tipo_normativa, nro_normativa, fecha, descripcion, categoria, organo_legislativo, jurisdiccion_id, palabras_clave):
        query = """
        INSERT INTO Normativa
        (Tipo_Normativa, Nro_Normativa, Fecha, Descripcion, Categoria, Organo_Legislativo, Jurisdiccion_ID)
        VALUES (?, ?, ?, ?, ?, ?, ?)
        """
        cursor = self.conn.cursor()
        
        if jurisdiccion_id == "Nacional":
            organo_legislativo = "Congreso de la Nacion"
        elif jurisdiccion_id == "Provincial":
            organo_legislativo = "Legislatura de Cordoba"
        else:
            print("Jurisdicción inválida. La normativa no será agregada.")
            return

        cursor.execute(query, (tipo_normativa, nro_normativa, fecha, descripcion, categoria, organo_legislativo, jurisdiccion_id))
        self.conn.commit()

        nro_registro = cursor.lastrowid
        self.agregar_palabras_clave(palabras_clave, nro_registro)

    def buscar_normativas_por_palabras_clave(self, palabras_clave):
        query = """
        SELECT *
        FROM Normativa
        WHERE Nro_Registro IN (
            SELECT DISTINCT Nro_Registro
            FROM PalabraClave
            WHERE Palabra IN ({})
        )
        """.format(",".join(["?"] * len(palabras_clave)))

        cursor = self.conn.execute(query, tuple(palabras_clave))
        return cursor.fetchall()

    def buscar_normativa_por_numero(self, numero_normativa):
        query = "SELECT * FROM Normativa WHERE Nro_Normativa = ?"
        cursor = self.conn.execute(query, (numero_normativa,))
        return cursor.fetchall()

    def mostrar_todas_normativas(self):
        query = "SELECT * FROM Normativa"
        cursor = self.conn.execute(query)
        return cursor.fetchall()

    def eliminar_normativa(self, nro_registro):
        query_palabra_clave = "DELETE FROM PalabraClave WHERE Nro_Registro = ?"
        query_normativa = "DELETE FROM Normativa WHERE Nro_Registro = ?"

        self.conn.execute(query_palabra_clave, (nro_registro,))
        self.conn.execute(query_normativa, (nro_registro,))
        self.conn.commit()

    def actualizar_descripcion_normativa(self, nro_registro, nueva_descripcion):
        query = "UPDATE Normativa SET Descripcion = ? WHERE Nro_Registro = ?"
        self.conn.execute(query, (nueva_descripcion, nro_registro))
        self.conn.commit()

    def agregar_palabras_clave(self, palabras_clave, nro_registro):
        query = "INSERT INTO PalabraClave (Palabra, Nro_Registro) VALUES (?, ?)"
        for palabra in palabras_clave:
            self.conn.execute(query, (palabra, nro_registro))
        self.conn.commit()


class ProgramaLeyes:
    def __init__(self):
        self.db = None

    def inicializar_db(self):
        nombre_db = "leyes.db"
        if not os.path.exists(nombre_db):
            self.db = LeyesDB(nombre_db)
            print("Base de datos creada y tablas creadas.")
        else:
            self.db = LeyesDB(nombre_db)
            print("Base de datos existente. Conectado a la base de datos.")

    def agregar_normativa(self):
        while True:
            tipo_normativa = input("Tipo de normativa (1: Ley, 2: Resolución, 3: Decreto): ")
            if tipo_normativa == "1":
                tipo_normativa = "Ley"
                break
            elif tipo_normativa == "2":
                tipo_normativa = "Resolución"
                break
            elif tipo_normativa == "3":
                tipo_normativa = "Decreto"
                break
            else:
                print("Opción inválida. Intente nuevamente.")
        nro_normativa = input("Número de normativa(Sin punto): ")
        fecha = input("Fecha (dd/mm/yyyy): ")
        descripcion = input("Descripción: ")
        while True:
            print("Categorías disponibles:")
            print("1. Laboral")
            print("2. Penal")
            print("3. Civil")
            print("4. Comercial")
            print("5. Familia y Sucesiones")
            print("6. Agrario y Ambiental")
            print("7. Minería")
            print("8. Derecho informático")
            categoria_opcion = input("Ingrese el número correspondiente a la categoría de la normativa: ")
            
            if categoria_opcion == "1":
                categoria = "Laboral"
                break
            elif categoria_opcion == "2":
                categoria = "Penal"
                break
            elif categoria_opcion == "3":
                categoria = "Civil"
                break
            elif categoria_opcion == "4":
                categoria = "Comercial"
                break
            elif categoria_opcion == "5":
                categoria = "Familia y Sucesiones"
                break
            elif categoria_opcion == "6":
                categoria = "Agrario y Ambiental"
                break
            elif categoria_opcion == "7":
                categoria = "Minería"
                break
            elif categoria_opcion == "8":
                categoria = "Derecho informático"
                break
            else:
                print("Opción inválida. Intente nuevamente.")
        jurisdiccion_nombre = input("Jurisdicción (Nacional o Provincial): ")
        palabras_clave = input("Palabras clave (separadas por comas): ").split(",")

        jurisdiccion_id = None
        if jurisdiccion_nombre.lower() == "nacional":
            jurisdiccion_id = "Nacional"
        elif jurisdiccion_nombre.lower() == "provincial":
            jurisdiccion_id = "Provincial"

        if jurisdiccion_id is None:
            print("Jurisdicción inválida. La normativa no será agregada.")
            return
        
        if jurisdiccion_id == "Nacional":
            organo_legislativo = "Congreso de la Nacion"
        elif jurisdiccion_id == "Provincial":
            organo_legislativo = "Legislatura de Cordoba"

        self.db.insertar_normativa(tipo_normativa, nro_normativa, fecha, descripcion, categoria, organo_legislativo, jurisdiccion_id, palabras_clave)
        print("Normativa agregada correctamente.")

    def buscar_normativas_por_palabras_clave(self):
        palabras_clave = input("Ingrese las palabras clave separadas por comas: ").split(",")
        normativas = self.db.buscar_normativas_por_palabras_clave(palabras_clave)

        if normativas:
            print("Normativas encontradas:")
            for normativa in normativas:
                print(normativa)
        else:
            print("No se encontraron normativas con las palabras clave proporcionadas.")

    def buscar_normativa_por_numero(self):
        numero_normativa = input("Ingrese el número de normativa (Sin punto): ")
        normativas = self.db.buscar_normativa_por_numero(numero_normativa)

        if normativas:
            print("Normativa encontrada:")
            for normativa in normativas:
                print(normativa)
        else:
            print("No se encontró la normativa con el número proporcionado.")

    def mostrar_todas_normativas(self):
        normativas = self.db.mostrar_todas_normativas()

        if normativas:
            print("Todas las normativas:")
            for normativa in normativas:
                print(normativa)
        else:
            print("No hay normativas en la base de datos.")

    def eliminar_normativa(self):
        nro_registro = input("Ingrese el número de registro de la normativa que desea eliminar: ")
        self.db.eliminar_normativa(nro_registro)
        print("Normativa eliminada correctamente.")

    def actualizar_descripcion_normativa(self):
        nro_registro = input("Ingrese el número de registro de la normativa que desea actualizar: ")
        nueva_descripcion = input("Ingrese la nueva descripción: ")
        self.db.actualizar_descripcion_normativa(nro_registro, nueva_descripcion)
        print("Descripción de la normativa actualizada correctamente.")


programa = ProgramaLeyes()
programa.inicializar_db()


while True:
    print("Poder Judicial de la Provincia de Córdoba")
    print("\n********** MENÚ **********")
    print("1. Agregar normativa")
    print("2. Buscar normativas por palabras clave")
    print("3. Buscar normativa por número")
    print("4. Mostrar todas las normativas")
    print("5. Eliminar normativa")
    print("6. Actualizar descripción de normativa")
    print("7. Salir")

    opcion = input("Ingrese una opción: ")

    if opcion == "1":
        programa.agregar_normativa()
    elif opcion == "2":
        programa.buscar_normativas_por_palabras_clave()
    elif opcion == "3":
        programa.buscar_normativa_por_numero()
    elif opcion == "4":
        programa.mostrar_todas_normativas()
    elif opcion == "5":
        programa.eliminar_normativa()
    elif opcion == "6":
        programa.actualizar_descripcion_normativa()
    elif opcion == "7":
        break
    else:
        print("Opción inválida. Intente nuevamente.")
