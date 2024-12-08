
import os
import pandas as pd
import numpy as np

current_dir = os.path.dirname(__file__)  # Directorio actual del script

input_dia_1 = os.path.join(current_dir, 'data', 'consolidated', '2024_12_04', 'ACEITE DE OLIVA.csv')
input_dia_2 = os.path.join(current_dir, 'data', 'consolidated', '2024_12_05', 'ACEITE DE OLIVA.csv')


def calcular_promedio_geometrico_precios(paths_csv):
    """
    Calcula el promedio geométrico de precios de productos 
    a partir de múltiples archivos CSV.
    
    Parámetros:
    paths_csv (list): Lista de rutas a los archivos CSV en orden cronológico
    
    Retorna:
    pd.DataFrame: DataFrame con productos y sus promedios geométricos
    """
    # Cargar todos los DataFrames
    dataframes = []
    for i, path in enumerate(paths_csv):
        df = pd.read_csv(path)
        # Añadir columna de día para referencia
        df['dia'] = i
        dataframes.append(df)
    
    # Concatenar todos los DataFrames
    df_concatenado = pd.concat(dataframes, ignore_index=True)
    
    # Calcular promedio geométrico
    def calcular_promedio_geo(grupo):
        precios = grupo['price_numeric'].dropna().tolist()
        if len(precios) > 0:
            promedio_geo = np.prod(precios) ** (1/len(precios))
            return pd.Series({
                'promedio_geometrico': round(promedio_geo, 2),
                'dias_disponibles': grupo['dia'].tolist(),
                'num_dias_disponibles': len(precios)
            })
        return pd.Series({
            'promedio_geometrico': np.nan,
            'dias_disponibles': [],
            'num_dias_disponibles': 0
        })
    
    # Agrupar por descripción y calcular
    resultados = df_concatenado.groupby('description').apply(calcular_promedio_geo).reset_index()
    
    # Filtrar solo productos con al menos un precio
    resultados = resultados[resultados['num_dias_disponibles'] > 0]
    
    # Ordenar por número de días disponibles y promedio geométrico
    resultados = resultados.sort_values(
        by=['num_dias_disponibles', 'promedio_geometrico'], 
        ascending=[False, True]
    )
    
    return resultados

# Ejemplo de uso
paths = [
    input_dia_1, 
    input_dia_2, 
]

# Llamar a la función
resultado = calcular_promedio_geometrico_precios(paths)
resultado.to_csv('resultado_seguimiento.csv', index=False, encoding='utf-8')

print(resultado)


# Información adicional
print("\nNúmero total de productos:", len(resultado))
print("Número de productos con precio en 1 día:", 
      len(resultado[resultado['num_dias_disponibles'] == 1]))
print("Número de productos con precio en 2 días:", 
      len(resultado[resultado['num_dias_disponibles'] == 2]))
print("Número de productos con precio en 3 días:", 
      len(resultado[resultado['num_dias_disponibles'] == 3]))
