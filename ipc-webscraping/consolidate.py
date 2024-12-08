import os
import pandas as pd
import numpy as np

from Levenshtein import distance as levenshtein_distance

def es_similar(texto1, texto2, umbral=0.8):
    """
    Comprueba si dos textos son similares usando la distancia de Levenshtein.
    """
    # Convertir a minúsculas y quitar espacios extras
    texto1 = str(texto1).lower().strip()
    texto2 = str(texto2).lower().strip()
    
    # Calcular la distancia de Levenshtein
    max_len = max(len(texto1), len(texto2))
    dist = levenshtein_distance(texto1, texto2)
    
    # Calcular similitud
    similitud = 1 - (dist / max_len)
    
    return similitud >= umbral

def eliminar_duplicados(df):
    """
    Elimina filas duplicadas basándose en la similitud de descripción,
    quedándose con el precio más bajo, pero solo si son de webs diferentes.
    """
    # Crear una copia del DataFrame
    df_procesado = df.copy()
    
    # Ordenar por price_numeric de manera ascendente para quedarnos con el precio más bajo
    df_procesado = df_procesado.sort_values('price_numeric', ascending=True)
    
    # Lista para almacenar índices de filas a eliminar
    indices_a_eliminar = []
    
    # Iterar por las filas
    for i in range(len(df_procesado)):
        if i in indices_a_eliminar:
            continue
        
        for j in range(i+1, len(df_procesado)):
            if j in indices_a_eliminar:
                continue
            
            # Verificar si son de webs diferentes
            if df_procesado.iloc[i]['WEB'] != df_procesado.iloc[j]['WEB']:
                # Verificar similitud de descripción
                if es_similar(df_procesado.iloc[i]['description_no_unit'], df_procesado.iloc[j]['description_no_unit']):
                    # Marcar la fila con precio más alto para eliminación
                    indices_a_eliminar.append(j)
    
    # Eliminar filas duplicadas
    df_procesado = df_procesado.drop(indices_a_eliminar)
    
    return df_procesado


def procesar_clasificaciones(df_clasificaciones, base_path, current_date, output_path):
    # Crear el directorio de salida si no existe
    os.makedirs(output_path, exist_ok=True)

    # Leer el archivo de web por producto
    current_dir = os.path.dirname(__file__)
    csv_path_prod_web = os.path.join(current_dir, 'base_period', 'Productos_x_web.csv')

    df_producto_web = pd.read_csv(csv_path_prod_web)
    
    
    # Iterar por cada fila del DataFrame de clasificaciones
    for _, fila in df_clasificaciones.iterrows():
        clasificacion = fila['CLASIFICACION']
        
        # Dataframe para consolidar los datos de esta clasificación
        df_clasificacion = pd.DataFrame()
        
        # Iterar por cada web
        webs = ['metro', 'plaza_vea', 'tottus', 'vega', 'vivanda', 'wong', 'tambo']
        for web in webs:
            # Construir la ruta del directorio
            input_path = os.path.join(base_path, 'data', 'processed', web, current_date)
            
            #ADICIONAL AQUI VERIFICAR SI ESE CSV SE VA TOMAR EN CUENTA SEGUN LA WEB

            # Verificar si la ruta existe
            if os.path.exists(input_path):
                # Buscar archivos CSV que contengan la clasificación en su nombre
                archivos_csv = [
                    archivo for archivo in os.listdir(input_path) 
                    if clasificacion.lower() in archivo.lower() and archivo.endswith('.csv')
                ]
                
                # Leer y consolidar cada CSV encontrado
                for archivo_csv in archivos_csv:
                    ruta_completa = os.path.join(input_path, archivo_csv)
                    try:
                        df_actual = pd.read_csv(ruta_completa)
                        # Agregar columna de web para trazabilidad
                        df_actual['WEB'] = web
                        

                        
                        # Verificamos si se mapea o no
                        nombre_producto = archivo_csv.split("_")[0]
                        fila_seleccionada = df_producto_web[df_producto_web["CLASIFICACION"] == nombre_producto]
                        valor_web = fila_seleccionada[web].iloc[0]


                        # Consolidar (solo si se mapeo que existe en la web)
                        if valor_web == "SI":
                            df_clasificacion = pd.concat([df_clasificacion, df_actual], ignore_index=True)
                        
                        
                    except Exception as e:
                        print(f"Error al leer {ruta_completa}: {e}")
        
        # Si se encontraron datos para esta clasificación
        if not df_clasificacion.empty:
            # Agregar columna de clasificación
            df_clasificacion['CLASIFICACION'] = clasificacion
            
            # Eliminar duplicados
            df_sin_duplicados = eliminar_duplicados(df_clasificacion)

            # Guardar con el nombre de la clasificación (reemplazando espacios por guiones bajos)
            nombre_archivo = f"{clasificacion}.csv"
            ruta_archivo = os.path.join(output_path, nombre_archivo)
            df_sin_duplicados.to_csv(ruta_archivo, index=False)
            print(f"Guardado {ruta_archivo} con {len(df_sin_duplicados)} filas")

# Uso del script
CURRENT_DATE = "2024_12_05"

current_dir = os.path.dirname(__file__)
csv_path = os.path.join(current_dir, 'base_period', 'IPC_BASE.csv')


# Cargar el CSV de clasificaciones
df_clasificaciones = pd.read_csv(csv_path)

# Especificar la ruta de salida
output_path = os.path.join(current_dir, 'data', 'consolidated', CURRENT_DATE)

# Procesar clasificaciones
procesar_clasificaciones(
    df_clasificaciones, 
    current_dir, 
    CURRENT_DATE,
    output_path
)