
# Devuelve un símbolo que indica el estado del menú
def simbolo(paso_requerido, paso_actual):
    if paso_actual <  paso_requerido: # Si el paso no se alcanzó
        return '✗'
    elif paso_actual == paso_requerido or (paso_requerido == 2 and paso_requerido < 3): # Si el paso se está ejecutando
        return '-'
    else: # Si el paso se completó
        return '✓'

def mostrar_menu(paso, datos, ruta):
    print("\n=============================")
    print("       Menú Principal       ")
    print("=============================")

    print(f"[{simbolo(1, paso)}] 1. Cargar datos ({'ningún archivo cargado' if paso <= 1 else f'archivo {ruta} cargado'})") 
     # Se necesitan datos para las siguientes funciones
    print(f"[{simbolo(2, paso)}] 2. Preprocesado de datos {'(requiere carga de datos)' if paso < 2 else '(selección de columnas requerida)' if paso == 2 else '(completado)' if paso >= 3 else ''}") 

    # Si ya se cargaron los datos se habilita el preprocesado
    if paso > 2:  
        print(f"\t[{simbolo(2.1, paso)}] 2.1 Selección de columnas ({'pendiente' if paso <= 2.1 else 'completado'})")
        print(f"\t[{simbolo(2.2, paso)}] 2.2 Manejo de valores faltantes ({'pendiente' if paso == 2.2 else 'requiere selección de columnas' if paso < 2.2 else 'completado'})")
        print(f"\t[{simbolo(2.3, paso)}] 2.3 Transformación de datos categóricos ({'pendiente' if paso == 2.3 else 'requiere manejo de valores faltantes' if paso < 2.3 else 'completado'})")
        print(f"\t[{simbolo(2.4, paso)}] 2.4 Normalización y escalado ({'pendiente' if paso == 2.4 else 'requiere transformación categórica' if paso < 2.4 else 'completado'})")
        print(f"\t[{simbolo(2.5, paso)}] 2.5 Detección y manejo de valores atípicos ({'pendiente' if paso == 2.5 else 'requiere normalización' if paso < 2.5 else 'completado'})")

    # Al finalizar el preprocesado se habilitan estas opciones
    print(f"[{simbolo(3, paso)}] 3. Visualización de datos ({'pendiente' if paso == 3 else 'requiere preprocesado completo' if paso < 3 else 'completado'})")  
    
    print(f"[{simbolo(4, paso)}] 4. Exportar datos ({'pendiente' if paso == 4 else 'requiere visualización de datos' if paso < 4 else 'completado'})")  
    
    print("[✓] 5. Salir")

    opcion = input("Seleccione una opción: ")
    return opcion

# Carga los datos dependiendo del tipo de archivo   
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

        opcion = int(input("Seleccione una opción: "))

        if opcion == 4: # Termina el bucle y vuelve al menú principal
            return   
        if opcion not in [1, 2, 3]: # Valida la opción
            print("Opción inválida. Intente de nuevo.")
        else:
            ruta = input("Ingrese la ruta del archivo: ")
            return (opcion, ruta)

# Muestra información sobre los datos       
def mostrar_datos(datos, fuente): 
    print("\nDatos cargados correctamente.")
    print(f"Fuente: {fuente}")
    print(f"Número de filas: {datos.shape[0]}")
    print(f"Número de columnas: {datos.shape[1]}")
    print(f"Tipo de datos por columna: ")
    print(datos.dtypes)
    print("\nPrimeras 5 filas:")
    print(datos.head())

# Selecciona las columnas de entrada y salida
def seleccion_terminal(columnas): 
    while True:
        # Mostrar las columnas disponibles para que el usuario seleccione las características
        print("\nSeleccione las columnas de entrada (features):")
        for i, columna in enumerate(columnas, 1): 
            print(f"  [{i}] {columna}")  
        
        # Solicita la entrada del usuario
        entrada = input("\nIngrese los números de las columnas de entrada (features), separados por comas: ")
        
        # Valida que las columnas estén dentro del rango
        indices_features = []
        indice_valido = True 
        
        try:
            for num in entrada.split(","):
                num = num.strip()
                if num.isdigit():
                    indice = int(num) - 1
                    if 0 <= indice < len(columnas):
                        if indice not in indices_features:
                            indices_features.append(indice)
                    else:
                        print(f"\nError: La columna '{num}' está fuera del rango. Debe seleccionar un número entre 1 y {len(columnas)}.")
                        indice_valido = False
                        break  # Si alguna columna está fuera de rango, reiniciamos la selección
                else:
                    print(f"\nError: '{num}' no es un número válido.")
                    indice_valido = False
                    break
        except ValueError:
            print("Entrada inválida. Asegúrese de ingresar números válidos separados por comas.")
            indice_valido = False

        # Si la entrada es inválida, le pedimos al usuario que intente de nuevo
        if not indice_valido or not indices_features:
            continue  

        # Muestra las columnas seleccionadas como features
        print("\nCaracterísticas seleccionadas:")
        for idx in indices_features:
            print(f"  - {columnas[idx]}")
        
        # Solicita al usuario que seleccione la columna target (de salida)
        while True:
            indice_target = obtener_indice_valido("Ingrese el número de la columna de salida (target): ", len(columnas))

            # Verifica que la columna target no esté ya en las features seleccionadas
            if indice_target in indices_features:
                print(f"\nError: La columna '{columnas[indice_target]}' ya está seleccionada como feature. Debe seleccionar un target que no esté en features")
            else:
                # Muestra la columna seleccionada como target
                print(f"\nColumna seleccionada como target: {columnas[indice_target]}")
                break  
        
        # Almacenamos las columnas seleccionadas
        features = [columnas[idx] for idx in indices_features]
        target = columnas[indice_target]

        return features, target
        
def obtener_indice_valido(mensaje, max_opciones):
    while True:
        try:
            entrada = int(input(mensaje))
            if 1 <= entrada <= max_opciones:
                return entrada - 1  # Devuelve el índice en base 0
            else:
                print(f"Debe ingresar un número entre 1 y {max_opciones}.")
        except ValueError:
            print("Entrada inválida. Intente de nuevo.")


# Cerrar la app de forma segura        
def cerrar(): 
    while True:
        print("\n=============================")
        print("     Salir de la Aplicación  ")
        print("=============================")
        print("¿Está seguro de que desea salir?")
        print("  [1] Sí")
        print("  [2] No")
        
        opcion = int(input("Seleccione una opción: "))
        
        if opcion == 1:
            print("\nCerrando la aplicación...")
            salir = True
            exit(0) # Termina el programa de forma exitosa 
        elif opcion == 2:
            print("\nRegresando al menú principal...")
            break
        else:
            print("\nOpción inválida. Intente de nuevo.")









