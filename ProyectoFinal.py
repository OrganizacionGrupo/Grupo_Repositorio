import sqlite3
import os


class LeyesDB:
    def __init__(self, nombre_db):
        self.conn = sqlite3.connect(nombre_db)
        self.crear_tablas()

    def crear_tablas(self):
        query_jurisdiccion = """
        CREATE TABLE IF NOT EXISTS Jurisdiccion (
            ID INTEGER PRIMARY KEY AUTOINCREMENT,
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
            Jurisdiccion_ID INTEGER NOT NULL,
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

        # Insertar jurisdicciones si no existen
        self.insertar_jurisdiccion(1, "Nacional")
        self.insertar_jurisdiccion(2, "Provincial")

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
        tipo_normativa = input("Tipo de normativa: ")
        nro_normativa = input("Número de normativa: ")
        fecha = input("Fecha: ")
        descripcion = input("Descripción: ")
        categoria = input("Categoría: ")
        organo_legislativo = input("Órgano legislativo: ")
        jurisdiccion_nombre = input("Jurisdicción (Nacional o Provincial): ")
        palabras_clave = input("Palabras clave (separadas por comas): ").split(",")

        jurisdiccion_id = None
        if jurisdiccion_nombre.lower() == "nacional":
            jurisdiccion_id = 1
        elif jurisdiccion_nombre.lower() == "provincial":
            jurisdiccion_id = 2

        if jurisdiccion_id is None:
            print("Jurisdicción inválida. La normativa no será agregada.")
            return

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
            print("No se encontraron normativas.")

    def mostrar_todas_normativas(self):
        normativas = self.db.mostrar_todas_normativas()

        if normativas:
            print("Todas las normativas:")
            for normativa in normativas:
                print(normativa)
        else:
            print("No se encontraron normativas.")

    def eliminar_normativa(self):
        nro_registro = input("Ingrese el número de registro de la normativa a eliminar: ")
        self.db.eliminar_normativa(nro_registro)
        print("Normativa eliminada correctamente.")

    def ejecutar(self):
        self.inicializar_db()
        while True:
            print("===== Menú =====")
            print("1. Agregar normativa")
            print("2. Buscar normativas por palabras clave")
            print("3. Mostrar todas las normativas")
            print("4. Eliminar normativa")
            print("5. Salir")
            opcion = input("Seleccione una opción: ")

            if opcion == "1":
                self.agregar_normativa()
            elif opcion == "2":
                self.buscar_normativas_por_palabras_clave()
            elif opcion == "3":
                self.mostrar_todas_normativas()
            elif opcion == "4":
                self.eliminar_normativa()
            elif opcion == "5":
                break
            else:
                print("Opción inválida. Intente nuevamente.")
                print(" ")


programa = ProgramaLeyes()
programa.ejecutar()

