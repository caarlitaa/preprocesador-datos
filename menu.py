def simbolo(paso_requerido, paso_actual):
    if paso_actual > paso_requerido:
        return '✓'
    elif paso_actual == paso_requerido:
        return '-'
    else:
        return '✗'

def mostrar_menu(paso):
    print("\n=============================")
    print("       Menú Principal       ")
    print("=============================")
    print(f"[{simbolo(1, paso)}] 1. Cargar datos") # Si los datos fueron cargados se muestra el tick
    print(f"[{simbolo(2, paso)}] 2. Preprocesado de datos") # Se necesitan datos para las siguientes funciones

    if paso > 2 and paso < 3:  # Si ya se cargaron los datos, habilitar el preprocesado
        print(f"\t[{simbolo(2.1, paso)}] 2.1 Selección de columnas")
        print(f"\t[{simbolo(2.2, paso)}] 2.2 Manejo de valores faltantes")
        print(f"\t[{simbolo(2.3, paso)}] 2.3 Transformación de datos categóricos")
        print(f"\t[{simbolo(2.4, paso)}] 2.4 Normalización y escalado")
        print(f"\t[{simbolo(2.5, paso)}] 2.5 Detección y manejo de valores atípicos")

    print(f"[{simbolo(3, paso)}] 3. Visualización de datos")  
    print(f"[{simbolo(4, paso)}] 4. Exportar datos")  
    print("[✓] 5. Salir")

    opcion = input("Seleccione una opción: ")
    return opcion
    
def cargar_datos():
    while True:
        print("\n=============================")
        print("       Carga de Datos       ")
        print("=============================")
        print("Seleccione el tipo de archivo a cargar:")
        print("  [1] CSV")
        print("  [2] Excel")
        print("  [3] SQLite")
        print("  [4] Volver al menú principal")

        opcion = (input("Seleccione una opción: "))

        if opcion == "4":
            return False  # Termina el bucle y vuelve al menú principal
        if opcion not in ["1","2","3"]:
            print("Opción inválida. Intente de nuevo.")
        else:
            ruta = input("Ingrese la ruta del archivo: ")
            return (opcion, ruta)
        
def mostrar_datos(datos, fuente):
    print("\nDatos cargados correctamente.")
    print(f"Fuente: {fuente}")
    print(f"Número de filas: {datos.shape[0]}")
    print(f"Número de columnas: {datos.shape[1]}")
    print("\nPrimeras 5 filas:")
    print(datos.head())

def seleccion_terminal(columnas):
    while True:
        # Mostrar las columnas disponibles para que el usuario seleccione las características
        print("\nSeleccione las columnas de entrada (features):")
        for i, col in enumerate(columnas, 1): 
            print(f"  [{i}] {col}")  
        
        # Solicitar la entrada del usuario
        entrada = input("\nIngrese los números de las columnas de entrada (features), separados por comas: ")
        
        # Convertir la entrada del usuario en una lista de índices
        try:
            indices_features = [int(x) - 1 for x in entrada.split(",")]  # Convertir a índices de columna (restando 1)
            if not indices_features:
                print("Debe seleccionar al menos una columna como feature.")
                continue
            # Mostrar las columnas seleccionadas como features
            print("\nCaracterísticas seleccionadas:")
            for idx in indices_features:
                print(f"  - {columnas[idx]}")
            
            # Solicitar al usuario que seleccione la columna target (de salida)
            while True:
                print("\nAhora seleccione la columna de salida (target):")
                indice_target = obtener_indice_valido("Ingrese el número de la columna de salida (target): ", len(columnas))

                # Verificar que la columna target no esté ya en las features seleccionadas
                if indice_target in indices_features:
                    print(f" \n Error: La columna '{columnas[indice_target]}' ya está seleccionada como feature. Debe seleccionar un target que no esté en features")
                else:
                    # Mostrar la columna seleccionada como target
                    print(f"\nColumna seleccionada como target: {columnas[indice_target]}")
                    break  # Salir del bucle de selección del target
            
            # Almacenamos las columnas seleccionadas
            features = [columnas[idx] for idx in indices_features]
            target = columnas[indice_target]

            return features, target
        except ValueError:
            print("Entrada inválida. Asegúrese de ingresar números válidos separados por comas.")
        
def obtener_indice_valido(mensaje, max_opciones):
    while True:
        try:
            entrada = int(input(mensaje))
            if 1 <= entrada <= max_opciones:
                return entrada - 1  # Devolver el índice en base 0
            else:
                print(f"Debe ingresar un número entre 1 y {max_opciones}.")
        except ValueError:
            print("Entrada inválida. Intente de nuevo.")

        
def cerrar():
    while True: # Se ejecuta mientras salir sea falso
        print("\n=============================")
        print("     Salir de la Aplicación  ")
        print("=============================")
        print("¿Está seguro de que desea salir?")
        print("  [1] Sí")
        print("  [2] No")
        
        opcion = int(input("Seleccione una opción: "))
        
        if opcion == 1:
            print("\nCerrando la aplicación...")
            exit(0) # Termina el programa de forma exitosa 
        elif opcion == 2:
            print("\nRegresando al menú principal...")
            break
        else:
            print("\nOpción inválida. Intente de nuevo.")









