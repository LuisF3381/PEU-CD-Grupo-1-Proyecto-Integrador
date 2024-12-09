import os
import pandas as pd
from datetime import datetime, timedelta

def concatenar_csvs(ruta_carpeta, fecha_inicio, fecha_fin):
    """
    Concatena archivos CSV dentro de un rango de fechas especificado.
    
    Parámetros:
    - ruta_carpeta: Ruta de la carpeta que contiene los CSV
    - fecha_inicio: Fecha de inicio del rango (formato 'YYYY_MM_DD')
    - fecha_fin: Fecha de fin del rango (formato 'YYYY_MM_DD')
    
    Retorna:
    - DataFrame concatenado con columna adicional de origen
    """
    # Convertir fechas de inicio y fin a objetos datetime
    fecha_inicio = datetime.strptime(fecha_inicio, '%Y_%m_%d')
    fecha_fin = datetime.strptime(fecha_fin, '%Y_%m_%d')
    
    # Lista para almacenar DataFrames
    dataframes = []
    
    # Iterar por fechas en el rango
    fecha_actual = fecha_inicio
    while fecha_actual <= fecha_fin:
        # Formatear nombre de carpeta
        nombre_carpeta = fecha_actual.strftime('%Y_%m_%d')
        ruta_directorio = os.path.join(ruta_carpeta, nombre_carpeta)
        
        # Verificar si el directorio existe
        if os.path.exists(ruta_directorio):
            # Listar todos los archivos CSV en el directorio
            for archivo_csv in os.listdir(ruta_directorio):
                if archivo_csv.endswith('.csv'):
                    ruta_csv = os.path.join(ruta_directorio, archivo_csv)
                    
                    # Leer CSV
                    df = pd.read_csv(ruta_csv)
                    
                    # Crear columna de origen sin la extensión .csv
                    origen = os.path.splitext(archivo_csv)[0]
                    
                    # Insertar columna de origen como primera columna
                    df.insert(0, 'categoria', origen)
                    
                    # Agregar a la lista de DataFrames
                    dataframes.append(df)
        
        # Avanzar al siguiente día
        fecha_actual += timedelta(days=1)
    
    # Concatenar DataFrames
    if dataframes:
        df_concatenado = pd.concat(dataframes, ignore_index=True)
        return df_concatenado
    else:
        print("No se encontraron archivos CSV en el rango de fechas especificado.")
        return None

# Ejemplo de uso
current_dir = os.path.dirname(__file__)
ruta_carpeta = os.path.join(current_dir, 'data', 'consolidated')



fecha_inicio = '2024_12_04'
fecha_fin = '2024_12_07'

# Concatenar CSVs
df_final = concatenar_csvs(ruta_carpeta, fecha_inicio, fecha_fin)

# Guardar resultado (opcional)
if df_final is not None:
    df_final.to_csv('datos_concatenados.csv', index=False)
    print(f"Archivo concatenado guardado. Número de filas: {len(df_final)}")
    print("Primeras filas del DataFrame concatenado:")
    print(df_final.head())