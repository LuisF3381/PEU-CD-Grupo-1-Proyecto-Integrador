import pandas as pd
import os

def consolidate_prices(csv_paths):
    """
    Consolida precios de múltiples archivos CSV en un único archivo.
    
    Parámetros:
    csv_paths (list): Lista de rutas de archivos CSV a consolidar
    
    Retorna:
    DataFrame consolidado con productos únicos y precios por día
    """
    # Lista para almacenar DataFrames de cada día
    daily_dataframes = []
    
    # Procesar cada CSV
    for day, path in enumerate(csv_paths, start=1):
        # Leer CSV
        df = pd.read_csv(path)
        
        # Crear columna de nombre de día
        df[f'price_day_{day}'] = df['price_numeric']
        
        # Agrupar por descripción, tomando el primer precio si hay duplicados
        daily_df = df.groupby('description').first().reset_index()
        daily_df = daily_df[['description', f'price_day_{day}']]
        
        daily_dataframes.append(daily_df)
    
    # Consolidar todos los DataFrames
    consolidated = daily_dataframes[0]
    for df in daily_dataframes[1:]:
        consolidated = pd.merge(consolidated, df, on='description', how='outer')
    
    # Reemplazar NaN con un valor por defecto (0 o None)
    consolidated = consolidated.fillna(0)
    
    return consolidated

def save_consolidated_csv(consolidated_df, output_path='consolidated_prices.csv'):
    """
    Guarda el DataFrame consolidado en un archivo CSV
    
    Parámetros:
    consolidated_df (DataFrame): DataFrame consolidado de precios
    output_path (str): Ruta de salida para el CSV consolidado
    """
    consolidated_df.to_csv(output_path, index=False)
    print(f"Archivo consolidado guardado en: {output_path}")

current_dir = os.path.dirname(__file__)  # Directorio actual del script

input_dia_1 = os.path.join(current_dir, 'data', 'consolidated', '2024_12_04', 'ACEITE DE OLIVA.csv')
input_dia_2 = os.path.join(current_dir, 'data', 'consolidated', '2024_12_05', 'ACEITE DE OLIVA.csv')


# Ejemplo de uso
csv_paths = [input_dia_1, input_dia_2]
result = consolidate_prices(csv_paths)
save_consolidated_csv(result)