
import os
import pandas as pd

CURRENT_DATE = "2024_12_04"



def extraer_volumen(df, archivo_no_procesados="no_procesados.csv"):
    """
    Extrae volumen de la descripción del producto con soporte para casos implícitos como 'x kg' o 'x ml'.
    Guarda las descripciones que no se pudieron procesar en un archivo CSV.

    Parámetros:
    df (pandas.DataFrame): DataFrame original
    archivo_no_procesados (str): Nombre del archivo CSV donde se guardarán las descripciones no procesadas

    Retorna:
    pandas.DataFrame: DataFrame con nuevas columnas de volumen (número y unidad)
    """
    # Expresión regular para capturar volumen
    regex = r'(\d+(?:\.\d+)?|x)\s*(ml|L|lt|g|gr|G|kg|Kg|KG|Kilo|oz|Onzas|Unid|unid|Unidades|un|Un|Porciones)'
    
    # Extraer número y unidad
    df[['cantidad', 'unidad']] = df['unit'].str.extract(regex)
    
    # Reemplazar "x" con 1 en cantidad
    df['cantidad'] = df['cantidad'].replace('x', 1).astype(float)
    
    # Filtrar las filas donde no se encontró volumen o unidad
    no_procesados = df[df['cantidad'].isna() | df['unidad'].isna()]
    
    # Si hay descripciones no procesadas, guardarlas en un archivo CSV
    if not no_procesados.empty:
        # Verificar si el archivo existe y apilar los nuevos datos
        if os.path.exists(archivo_no_procesados):
            no_procesados[['unit']].to_csv(archivo_no_procesados, mode='a', header=False, index=False)
        else:
            no_procesados[['unit']].to_csv(archivo_no_procesados, mode='w', header=True, index=False)
    
    return df

def estandarizar_unidades(df: pd.DataFrame) -> pd.DataFrame:
    # Definimos un diccionario con las reglas de reemplazo
    reglas_reemplazo = {
        'L': 'l', 'lt': 'l',  # L o lt deben ser reemplazados por l
        'g': 'g', 'gr': 'g', 'G': 'g',  # g, gr o G deben ser reemplazados por g
        'kg': 'kg', 'Kg': 'kg', 'Kilo': 'kg', 'KG':'kg',  # kg, Kg o Kilo deben ser reemplazados por kg
        'oz': 'oz', 'Onzas': 'oz',  # oz o Onzas deben ser reemplazados por oz
        'Unid': 'un', 'unid': 'un', 'Unidades': 'un', 'un': 'un', 'Un': 'un', 'Porciones': 'un'  # Varias formas de "un" o "Porciones"
    }
    
    # Aplicamos el reemplazo
    df['unidad'] = df['unidad'].replace(reglas_reemplazo)
    
    return df


def eliminar_filas_sin_unidad(df):
    """
    Elimina filas donde la unidad de volumen es nula.

    Parámetros:
    df (pandas.DataFrame): DataFrame original

    Retorna:
    pandas.DataFrame: DataFrame sin filas con unidad nula
    """
    return df[df['unidad'].notna()]


def extraer_precio_numerico(df):
    """
    Extrae el valor numérico de la columna price.

    Parámetros:
    df (pandas.DataFrame): DataFrame original

    Retorna:
    pandas.DataFrame: DataFrame con nueva columna price_numeric
    """
    df['price_numeric'] = df['price'].str.extract(r'S/\s*([\d.]+)')[0].astype(float)
    return df


def primer_procesamiento(df):
 
    df = extraer_volumen(df)
    df = eliminar_filas_sin_unidad(df)
    # Arreglar las unidades
    df = estandarizar_unidades(df)
        
    # Extraemos el precio
    df = extraer_precio_numerico(df)
    return df



current_dir = os.path.dirname(__file__)  # Directorio actual del script
input_path = os.path.join(current_dir, 'data', 'raw','plaza_vea', CURRENT_DATE)
output_path = os.path.join(current_dir, 'data', 'processed','plaza_vea', CURRENT_DATE)
os.makedirs(output_path, exist_ok=True)  # Crea la carpeta si no existe


# Ahora iteramos para todos los archivos de esa fecha
for filename in os.listdir(input_path):
    if filename.endswith('.csv'):
        file_path = os.path.join(input_path, filename)
        try:
            # Leemos el archivo
            df = pd.read_csv(file_path)

            # Primer procesamiento
            df = primer_procesamiento(df)

            # Extraemos el nombre modificado
            parts = filename.split('_')
            new_name = f"{parts[2]}_{parts[3]}"  # Extrae 'ACEITE DE OLIVA' y '20241203'

            # Guardamos el archivo procesado con el nuevo nombre
            output_file_path = os.path.join(output_path, f'{new_name}.csv')
            df.to_csv(output_file_path, index=False)
            
            print(f'Archivo procesado y guardado en: {output_file_path}')
        except Exception as e:
            print(e)
        # Segundo procesamiento
        #print(f'Contents of {filename}:')
        #print(df)
        #print()




