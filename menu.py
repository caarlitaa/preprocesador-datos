
def menu():
    salir = False
    while not salir:
        print("\n=============================")
        print("       Menú Principal       ")
        print("=============================")
        print("[1] Cargar datos")
        print("[2] Preprocesado de datos")
        print("      [2.1] Selección de columnas")
        print("      [2.2] Manejo de valores faltantes")
        print("      [2.3] Transformación de datos categóricos")
        print("      [2.4] Normalización y escalado")
        print("      [2.5] Detección y manejo de valores atípicos")
        print("[3] Visualización de datos")
        print("[4] Exportar datos")
        print("[5] Salir")

        opcion = int(input("Seleccione una opción: "))
        
        if opcion == 5:
            cerrar()  # Llama a la función de cierre seguro
            salir = True  
        
def cerrar():
    salir = False 
    while not salir: # Se ejecuta mientras salir sea falso5
        print("\n=============================")
        print("     Salir de la Aplicación  ")
        print("=============================")
        print("¿Está seguro de que desea salir?")
        print("  [1] Sí")
        print("  [2] No")
        
        opcion = int(input("Seleccione una opción: "))
        
        if opcion == 1:
            print("\nCerrando la aplicación...")
            exit(0)  
        elif opcion == 2:
            print("\nRegresando al menú principal...")
            salir = True  # Cambia la variable para salir del bucle
        else:
            print("\nOpción inválida. Intente de nuevo.")





