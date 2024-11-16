import pymongo
from pymongo import MongoClient

# Conexión a MongoDB
client = MongoClient('mongodb://localhost:27017/')
db = client['torneoTenisDeMesa']

# Funciones CRUD para Jugadores, Árbitros y Partidas

# Función para crear un jugador
def crear_jugador():
    nombre = input("Ingrese el nombre del jugador: ")
    id_jugador = int(input("Ingrese el ID del jugador: "))
    edad = int(input("Ingrese la edad del jugador: "))
    pais = input("Ingrese el país del jugador: ")

    jugador = {
        "nombre": nombre,
        "id": id_jugador,
        "edad": edad,
        "pais": pais
    }

    db.jugador.insert_one(jugador)
    print(f"Jugador {nombre} creado correctamente.\n")

# Funcion para crear un arbitro
def crear_arbitro():
    nombre = input("Ingrese el nombre del arbitro: ")
    id_jugador = int(input("Ingrese el ID del arbitro: "))
    edad = int(input("Ingrese la edad del arbitro: "))
    pais = input("Ingrese el país del arbitro: ")

    arbitro = {
        "nombre": nombre,
        "id": id_jugador,
        "edad": edad,
        "pais": pais
    }

    db.arbitro.insert_one(arbitro)
    print(f"Arbitro {nombre} creado correctamente.\n")

# Función para crear una partida
def crear_partida():
    fecha = input("Ingrese la fecha y hora del juego (formato: YYYY-MM-DD HH:MM): ")
    nombre_jugador1 = input("Ingrese el nombre del Jugador 1: ")
    nombre_jugador2 = input("Ingrese el nombre del Jugador 2: ")
    arbitro = input("Ingrese el nombre del árbitro: ")

    # Función para pedir y verificar los puntos de un set
    def pedir_puntos_set(set_num):
        while True:
            try:
                puntos = input(f"Ingrese los puntos del Set {set_num} (formato: jugador1,jugador2): ").split(",")
                if len(puntos) != 2:  # Verifica si hay exactamente dos elementos
                    print("Error: Debe ingresar dos valores, separados por una coma.")
                    continue
                puntos = [int(puntos[0]), int(puntos[1])]  # Convertir a enteros
                return puntos
            except ValueError:
                print("Error: Asegúrese de ingresar números válidos, separados por una coma.")
                continue

    # Solicitar los puntos de cada set con la función de verificación
    puntos_set1 = pedir_puntos_set(1)
    puntos_set2 = pedir_puntos_set(2)
    puntos_set3 = pedir_puntos_set(3)
    puntos_set4 = pedir_puntos_set(4)

    # Crear el documento de la partida
    partida = {
        "fecha_juego": fecha,
        "nombre_jugador1": nombre_jugador1,
        "nombre_jugador2": nombre_jugador2,
        "arbitro": arbitro,
        "puntos_set1": puntos_set1,
        "puntos_set2": puntos_set2,
        "puntos_set3": puntos_set3,
        "puntos_set4": puntos_set4
    }

    # Insertar la partida en la base de datos
    db.partido.insert_one(partida)
    print("Partida creada correctamente.\n")

# Función para leer jugadores
def leer_jugadores():
    jugadores = db.jugador.find()
    for jugador in jugadores:
        print(jugador)
    print()

# Funcion para leer arbitros
def leer_arbitros():
    arbitros = db.arbitro.find()
    for arbitro in arbitros:
        print(arbitro)
    print()


# Funcion para leer la tabla de posiciones
def leer_tablaposiciones():
    try:
        partidas = db.partido.find()

        # Diccionario para almacenar estadísticas de los jugadores
        estadisticas = {}

        for partida in partidas:
            nombre_jugador1 = partida['nombre_jugador1']
            nombre_jugador2 = partida['nombre_jugador2']
            puntos_j1 = sum(partida['puntos_set1']) + sum(partida['puntos_set2']) + sum(partida['puntos_set3']) + sum(partida['puntos_set4'])
            puntos_j2 = sum(partida['puntos_set1'][::-1]) + sum(partida['puntos_set2'][::-1]) + sum(partida['puntos_set3'][::-1]) + sum(partida['puntos_set4'][::-1])

            # Si los jugadores no están en el diccionario, inicializarlos
            if nombre_jugador1 not in estadisticas:
                estadisticas[nombre_jugador1] = {'victorias': 0, 'derrotas': 0, 'partidas_jugadas': 0}
            if nombre_jugador2 not in estadisticas:
                estadisticas[nombre_jugador2] = {'victorias': 0, 'derrotas': 0, 'partidas_jugadas': 0}

            # Actualizar el número de partidas jugadas
            estadisticas[nombre_jugador1]['partidas_jugadas'] += 1
            estadisticas[nombre_jugador2]['partidas_jugadas'] += 1

            # Determinar el ganador y actualizar victorias/derrotas
            if puntos_j1 > puntos_j2:
                estadisticas[nombre_jugador1]['victorias'] += 1
                estadisticas[nombre_jugador2]['derrotas'] += 1
            else:
                estadisticas[nombre_jugador2]['victorias'] += 1
                estadisticas[nombre_jugador1]['derrotas'] += 1

        # Ordenar jugadores por número de victorias
        jugadores_ordenados = sorted(estadisticas.items(), key=lambda x: x[1]['victorias'], reverse=True)

        # Actualizar la tabla de posiciones en la base de datos
        for posicion, (nombre, datos) in enumerate(jugadores_ordenados, start=1):
            # Actualizar la posición del jugador en la colección
            db.tablaPosiciones.update_one(
                {'nombre': nombre},  # Filtro para encontrar al jugador por su nombre
                {'$set': {
                    'posicion': posicion,
                    'victorias': datos['victorias'],
                    'derrotas': datos['derrotas'],
                    'partidas_jugadas': datos['partidas_jugadas']
                }},
                upsert=True  # Si no se encuentra el jugador, lo crea
            )

        print("\n--- Tabla de Posiciones ---")
        for posicion, (nombre, datos) in enumerate(jugadores_ordenados, start=1):
            print(f"{posicion}. {nombre} - Victorias: {datos['victorias']}, Derrotas: {datos['derrotas']}, Partidas Jugadas: {datos['partidas_jugadas']}")

    except Exception as e:
        print("Ocurrió un error al leer la tabla de posiciones:", e)

def resultados_partida():
    partidas = db.partido.find()

    for partida in partidas:
        fecha = partida['fecha_juego']
        nombre_jugador1 = partida['nombre_jugador1']
        nombre_jugador2 = partida['nombre_jugador2']
        arbitro = partida['arbitro']

        # Calcular los sets ganados por cada jugador
        sets_ganados_j1 = sum(1 for set_puntos in [partida['puntos_set1'], partida['puntos_set2'], partida['puntos_set3'], partida['puntos_set4']] if set_puntos[0] > set_puntos[1])
        sets_ganados_j2 = sum(1 for set_puntos in [partida['puntos_set1'], partida['puntos_set2'], partida['puntos_set3'], partida['puntos_set4']] if set_puntos[1] > set_puntos[0])

        # Determinar el ganador y el perdedor
        if sets_ganados_j1 > sets_ganados_j2:
            ganador = nombre_jugador1
            sets_ganados = sets_ganados_j1
            perdedor = nombre_jugador2
            sets_perdedor = sets_ganados_j2
        else:
            ganador = nombre_jugador2
            sets_ganados = sets_ganados_j2
            perdedor = nombre_jugador1
            sets_perdedor = sets_ganados_j1

        # Imprimir resultados
        print(f"Fecha y hora del juego: {fecha}")
        print(f"Ganador: {ganador} (Sets ganados: {sets_ganados})")
        print(f"Perdedor: {perdedor} (Sets ganados: {sets_perdedor})")
        print(f"Árbitro: {arbitro}")
        print("--------------------------------------")



# Función para actualizar un jugador
def actualizar_jugador():
    id_jugador = int(input("Ingrese el ID del jugador a actualizar: "))
    jugador = db.jugador.find_one({"id": id_jugador})

    if jugador:
        print(f"Jugador encontrado: {jugador['nombre']}")
        nombre = input("Ingrese el nuevo nombre (dejar vacío para no cambiar): ")
        edad = input("Ingrese la nueva edad (dejar vacío para no cambiar): ")
        pais = input("Ingrese el nuevo país (dejar vacío para no cambiar): ")

        update_data = {}
        if nombre:
            update_data["nombre"] = nombre
        if edad:
            update_data["edad"] = int(edad)
        if pais:
            update_data["pais"] = pais

        db.jugador.update_one({"id": id_jugador}, {"$set": update_data})
        print(f"Jugador con ID {id_jugador} actualizado.\n")
    else:
        print("Jugador no encontrado.\n")

# Funcion para actualizar un arbitro
def actualizar_arbitro():
    id_arbitro = int(input("Ingrese el ID del arbitro a actualizar: "))
    arbitro = db.arbitro.find_one({"id":id_arbitro})

    if arbitro:
        print(f"Arbitro encontrado: {arbitro['nombre']}")
        nombre = input("Ingrese el nuevo nombre (dejar vacío para no cambiar): ")
        edad = input("Ingrese la nueva edad (dejar vacío para no cambiar): ")
        pais = input("Ingrese el nuevo país (dejar vacío para no cambiar): ")

        update_data = {}
        if nombre:
            update_data["nombre"] = nombre
        if edad:
            update_data["edad"] = int(edad)
        if pais:
            update_data["pais"] = pais

        db.arbitro.update_one({"id": id_arbitro}, {"$set": update_data})
        print(f"Arbitro con ID {id_arbitro} actualizado.\n")
    else:
        print("Arbitro no encontrado.\n")

# Función para modificar una partida existente
def actualizar_partida():
    try:
        # Mostrar todas las partidas existentes
        partidas = list(db.partido.find())
        if not partidas:
            print("No hay partidas registradas para modificar.")
            return

        print("\n--- Partidas Registradas ---")
        for idx, partida in enumerate(partidas, start=1):
            print(f"{idx}. Fecha: {partida['fecha_juego']}, Jugador 1: {partida['nombre_jugador1']}, Jugador 2: {partida['nombre_jugador2']}")

        # Seleccionar la partida a modificar
        num_partida = int(input("\nSeleccione el número de la partida que desea modificar: "))
        if num_partida < 1 or num_partida > len(partidas):
            print("Número de partida inválido.")
            return

        partida_a_modificar = partidas[num_partida - 1]

        # Solicitar nuevos valores
        print("\n--- Ingrese los nuevos valores (deje en blanco para mantener el valor actual) ---")
        nueva_fecha = input(f"Nueva fecha y hora (actual: {partida_a_modificar['fecha_juego']}): ") or partida_a_modificar['fecha_juego']
        nuevo_jugador1 = input(f"Nuevo nombre del Jugador 1 (actual: {partida_a_modificar['nombre_jugador1']}): ") or partida_a_modificar['nombre_jugador1']
        nuevo_jugador2 = input(f"Nuevo nombre del Jugador 2 (actual: {partida_a_modificar['nombre_jugador2']}): ") or partida_a_modificar['nombre_jugador2']
        nuevo_arbitro = input(f"Nuevo nombre del árbitro (actual: {partida_a_modificar['arbitro']}): ") or partida_a_modificar['arbitro']

        # Solicitar nuevos puntos de los sets
        def pedir_puntos_modificados(set_num, puntos_actuales):
            nuevos_puntos = input(f"Nuevos puntos del Set {set_num} (actual: {puntos_actuales}, formato: jugador1,jugador2): ")
            if nuevos_puntos:
                try:
                    puntos = nuevos_puntos.split(",")
                    if len(puntos) != 2:
                        print("Error: Debe ingresar dos valores, separados por una coma.")
                        return puntos_actuales
                    return [int(puntos[0]), int(puntos[1])]
                except ValueError:
                    print("Error: Asegúrese de ingresar números válidos.")
                    return puntos_actuales
            else:
                return puntos_actuales

        puntos_set1 = pedir_puntos_modificados(1, partida_a_modificar['puntos_set1'])
        puntos_set2 = pedir_puntos_modificados(2, partida_a_modificar['puntos_set2'])
        puntos_set3 = pedir_puntos_modificados(3, partida_a_modificar['puntos_set3'])
        puntos_set4 = pedir_puntos_modificados(4, partida_a_modificar['puntos_set4'])

        # Actualizar la partida
        db.partido.update_one(
            {"_id": partida_a_modificar["_id"]},
            {"$set": {
                "fecha_juego": nueva_fecha,
                "nombre_jugador1": nuevo_jugador1,
                "nombre_jugador2": nuevo_jugador2,
                "arbitro": nuevo_arbitro,
                "puntos_set1": puntos_set1,
                "puntos_set2": puntos_set2,
                "puntos_set3": puntos_set3,
                "puntos_set4": puntos_set4
            }}
        )
        print("Partida modificada correctamente.")

    except Exception as e:
        print("Ocurrió un error al modificar la partida:", e)


# Función para eliminar un jugador
def eliminar_jugador():
    id_jugador = int(input("Ingrese el ID del jugador a eliminar: "))
    result = db.jugador.delete_one({"id": id_jugador})

    if result.deleted_count > 0:
        print(f"Jugador con ID {id_jugador} eliminado.\n")
    else:
        print("Jugador no encontrado.\n")

# Funcion para eliminar un arbitro
def eliminar_arbitro():
    id_arbitro = int(input("Ingrese el ID del arbitro a eliminar: "))
    result = db.arbitro.delete_one({"id": id_arbitro})

    if result.deleted_count > 0:
        print(f"Arbitro con ID {id_arbitro} eliminado.\n")
    else:
        print("Arbitro no encontrado.\n")

# Función para eliminar una partida existente
def eliminar_partida():
    try:
        # Mostrar todas las partidas existentes
        partidas = list(db.partido.find())
        if not partidas:
            print("No hay partidas registradas para eliminar.")
            return

        print("\n--- Partidas Registradas ---")
        for idx, partida in enumerate(partidas, start=1):
            print(f"{idx}. Fecha: {partida['fecha_juego']}, Jugador 1: {partida['nombre_jugador1']}, Jugador 2: {partida['nombre_jugador2']}")

        # Seleccionar la partida a eliminar
        num_partida = int(input("\nSeleccione el número de la partida que desea eliminar: "))
        if num_partida < 1 or num_partida > len(partidas):
            print("Número de partida inválido.")
            return

        partida_a_eliminar = partidas[num_partida - 1]
        db.partido.delete_one({"_id": partida_a_eliminar["_id"]})
        print("Partida eliminada correctamente.")



    except Exception as e:
        print("Ocurrió un error al eliminar la partida:", e)

# Función para mostrar el menú
def mostrar_menu():
    while True:
        print("Menú Principal:")
        print("1. Crear")
        print("2. Leer")
        print("3. Actualizar")
        print("4. Eliminar")
        print("5. Salir")

        opcion = input("Seleccione una opción: ")

        if opcion == "1":
            mostrar_submenu_crear()
        elif opcion == "2":
            mostrar_submenu_leer()
        elif opcion == "3":
            mostrar_submenu_actualizar()
        elif opcion == "4":
            mostrar_submenu_eliminar()
        elif opcion == "5":
            break
        else:
            print("Opción no válida. Intente nuevamente.\n")

# Función para mostrar el submenú de "Crear"
def mostrar_submenu_crear():
    print("\nSubmenú Crear:")
    print("1. Crear Jugador")
    print("2. Crear Árbitro")
    print("3. Crear Partida")
    print("4. Volver al Menú Principal")

    opcion = input("Seleccione una opción: ")

    if opcion == "1":
        crear_jugador()
    elif opcion == "2":
        crear_arbitro()
    elif opcion == "3":
        crear_partida()
    elif opcion == "4":
        return
    else:
        print("Opción no válida. Intente nuevamente.\n")

# Función para mostrar el submenú de "Leer"
def mostrar_submenu_leer():
    print("\nSubmenú Leer:")
    print("1. Leer Jugadores")
    print("2. Leer Arbitros")
    print("3. Leer Partidas")
    print("4. Tabla de posiciones")
    print("5. Resultados de partida")
    print("6. Volver al Menú Principal")

    opcion = input("Seleccione una opción: ")

    if opcion == "1":
        leer_jugadores()
    elif opcion == "2":
        leer_arbitros()
    elif opcion == "3":
        leer_partidas()
    elif opcion == "4":
        leer_tablaposiciones()
    elif opcion == "5":
        resultados_partida()
    elif opcion == "6":
        return
    else:
        print("Opción no válida. Intente nuevamente.\n")

# Función para mostrar el submenú de "Actualizar"
def mostrar_submenu_actualizar():
    print("\nSubmenú Actualizar:")
    print("1. Actualizar Jugador")
    print("2. Actualizar Arbitro")
    print("3. Actualizar Partida")
    print("4. Volver al Menú Principal")

    opcion = input("Seleccione una opción: ")

    if opcion == "1":
        actualizar_jugador()
    elif opcion == "2":
        actualizar_arbitro()
    elif opcion == "3":
        actualizar_partida()
    elif opcion == "4":
        return
    else:
        print("Opción no válida. Intente nuevamente.\n")

# Función para mostrar el submenú de "Eliminar"
def mostrar_submenu_eliminar():
    print("\nSubmenú Eliminar:")
    print("1. Eliminar Jugador")
    print("2. Eliminar Arbitro")
    print("3. Eliminar Partida")
    print("4. Volver al Menú Principal")

    opcion = input("Seleccione una opción: ")

    if opcion == "1":
        eliminar_jugador()
    elif opcion == "2":
        eliminar_arbitro()
    elif opcion == "3":
        eliminar_partida()
    elif opcion == "4":
        return
    else:
        print("Opción no válida. Intente nuevamente.\n")

# Iniciar el menú
if __name__ == "__main__":
    mostrar_menu()


