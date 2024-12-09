import os
import pandas as pd
import numpy as np
import utils_preprocess


from Levenshtein import distance as levenshtein_distance

def escalar_unidades(df, unidad_escalamiento, cantidad_escalamiento):
    """
    Escala las unidades, cantidades y precios de un DataFrame según una nueva unidad y cantidad objetivo.
    Elimina las filas donde las unidades no sean convertibles o haya errores en la conversión.
    """
    # Diccionario de factores de conversión entre unidades
    conversion_factors = {
        ('g', 'kg'): 1000,
        ('kg', 'g'): 0.001,
        ('ml', 'l'): 1000,
        ('l', 'ml'): 0.001,
        ('g', 'g'): 1,
        ('kg', 'kg'): 1,
        ('ml', 'ml'): 1,
        ('l', 'l'): 1,
    }
    
    # Crear una copia del DataFrame
    df = df.copy()
    
    # Caso especial: Sin escalamiento (valores originales)
    if unidad_escalamiento == "0" and cantidad_escalamiento == 0:
        df['unidad_escalada'] = df['unidad']
        df['cantidad_escalada'] = df['cantidad']
        df['price_numeric_escalado'] = df['price_numeric']
        return df
    
    def convertir_fila(row):
        # Verificaciones de seguridad
        if pd.isna(row['unidad']) or pd.isna(row['cantidad']) or row['cantidad'] == 0:
            return pd.Series([None, None, None])
        
        # Verifica si la unidad actual está en las claves de los factores de conversión
        if (row['unidad'], unidad_escalamiento) not in conversion_factors:
            return pd.Series([None, None, None])
        
        # Obtener el factor de conversión entre la unidad original y la unidad escalada
        factor_conversion = conversion_factors.get((row['unidad'], unidad_escalamiento))
        
        # Manejar caso de factor de conversión cero
        if factor_conversion == 0:
            return pd.Series([None, None, None])
        
        try:
            # Calcular cantidad escalada
            cantidad_original_en_unidad_objetivo = row['cantidad'] / factor_conversion
            cantidad_escalada = cantidad_escalamiento
            
            # Escalar el precio proporcionalmente
            price_numeric_escalado = row['price_numeric'] * (cantidad_escalada / cantidad_original_en_unidad_objetivo)
            
            return pd.Series([unidad_escalamiento, cantidad_escalada, price_numeric_escalado])
        
        except Exception as e:
            # Mejor manejo de errores con log y retorno de nulos
            print(f"Error en conversión en la fila con unidad '{row['unidad']}': {e}")
            return pd.Series([None, None, None])
    
    # Aplicar las conversiones
    resultados = df.apply(convertir_fila, axis=1)
    
    # Asignar las columnas de manera explícita
    df['unidad_escalada'] = resultados[0]
    df['cantidad_escalada'] = resultados[1]
    df['price_numeric_escalado'] = resultados[2]
    
    # Eliminar filas no escalables (con valores nulos en cantidad y precio)
    df = df.dropna(subset=['cantidad_escalada', 'price_numeric_escalado']).reset_index(drop=True)
    
    return df



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

    # Leer el archivo de unidades
    csv_path_prod_unid = os.path.join(current_dir, 'base_period', 'IPC_BASE_unid.csv')
    df_unidades = pd.read_csv(csv_path_prod_unid)

    #print(df_unidades)
    
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
                        
                        nombre_producto = archivo_csv.split("_")[0]

                        # Verificamos si se mapea o no 
                        fila_seleccionada = df_producto_web[df_producto_web["CLASIFICACION"] == nombre_producto]
                        valor_web = fila_seleccionada[web].iloc[0]


                        # Consolidar (solo si se mapeo que existe en la web)
                        if valor_web == "SI":
                            # Aqui hacemos el reescalamiento de unidades
                            fila_seleccionada_esc = df_unidades[df_unidades["CLASIFICACION"] == nombre_producto]
                            unidad = fila_seleccionada_esc["unidad"].iloc[0]
                            cantidad = fila_seleccionada_esc["cantidad"].iloc[0]
                            
                            df_actual = escalar_unidades(df_actual, unidad, cantidad)

                            df_clasificacion = pd.concat([df_clasificacion, df_actual], ignore_index=True)
                        
                        
                    except Exception as e:
                        print(f"Error al tratar con {ruta_completa}: {e}")
        
        # Si se encontraron datos para esta clasificación
        if not df_clasificacion.empty:
            # Agregar columna de clasificación
            df_clasificacion['CLASIFICACION'] = clasificacion
            
            # Eliminar duplicados
            df_sin_duplicados = eliminar_duplicados(df_clasificacion)

            # Asegúrate de que la columna 'brand' esté en el DataFrame, incluso si no existe
            if 'brand' not in df_sin_duplicados.columns:
                df_sin_duplicados['brand'] = np.nan

            # Seleccionamos las columnas relevantes
            columnas_seleccionadas = ['description', 'brand', 'cantidad', 'unidad', 'price_numeric', 'website', 'scrape_timestamp', 'search_term', 'cantidad_escalada', 'unidad_escalada', 'price_numeric_escalado', 'CLASIFICACION']
            df_sin_duplicados = df_sin_duplicados[columnas_seleccionadas]
            
            # Aplicamos la funcion de filro correspondiente
            print("Ga aqui:",clasificacion)

            # Leeemos el csv
            current_dir = os.path.dirname(__file__)
            csv_procesamiento = os.path.join(current_dir, 'base_period', 'Procesamiento.csv')
            df_procesamiento = pd.read_csv(csv_procesamiento)

            funcion_row = df_procesamiento[df_procesamiento['PRODUCTO'] == clasificacion]
            #print(funcion_row)

            # Supongamos que ya tienes la variable 'funcion_row' con los datos
            if pd.isna(funcion_row['terminos'].iloc[0]) or pd.isna(funcion_row['funcion_tratamiento'].iloc[0]):
                print("El valor de 'terminos' o 'funcion_tratamiento' es NaN. NO SE APLICARA FILTRO")
            else:
                funcion_nombre = funcion_row['funcion_tratamiento'].iloc[0]
                terminos = funcion_row['terminos'].iloc[0]

                funcion_tratamiento = getattr(utils_preprocess, funcion_nombre)

                df_sin_duplicados = funcion_tratamiento(df_sin_duplicados, terminos)


            # Guardar con el nombre de la clasificación (reemplazando espacios por guiones bajos)
            nombre_archivo = f"{clasificacion}.csv"
            ruta_archivo = os.path.join(output_path, nombre_archivo)
            
            if not df_sin_duplicados.empty:
                df_sin_duplicados.to_csv(ruta_archivo, index=False)
                print(f"Guardado {ruta_archivo} con {len(df_sin_duplicados)} filas")
            else:
                print("El DataFrame está vacío, no se guardará el archivo.")

# Uso del script
CURRENT_DATE = "2024_12_04"

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