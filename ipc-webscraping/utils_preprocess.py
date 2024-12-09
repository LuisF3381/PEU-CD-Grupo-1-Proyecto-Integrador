import os
import pandas as pd
import re

# funciones en comun para el procesamiento de las cedenas de descripcion
def todos_terminos_presentes_primero_al_inicio(df, terminos):
    """
    Filtra las filas de un DataFrame donde todos los términos están presentes en la columna 'description',
    y el primer término aparece al principio de la cadena, ignorando mayúsculas y minúsculas.

    Args:
        df (pd.DataFrame): El DataFrame con los datos.
        terminos (str): Una cadena con los términos separados por espacios.

    Returns:
        pd.DataFrame: Un nuevo DataFrame filtrado.
    """
    terminos_lista = [termino.lower() for termino in terminos.split()]
    
    # Filtrar las filas donde todos los términos están en 'description'
    df_filtrado = df[df['description'].apply(
        lambda x: x.lower().startswith(terminos_lista[0]) and all(termino in x.lower() for termino in terminos_lista)
    )]
    
    return df_filtrado.reset_index(drop=True)


def todos_terminos_presentes(df, terminos):
    """
    Filtra las filas de un DataFrame donde todos los términos están presentes en la columna 'description',
    ignorando mayúsculas y minúsculas.

    Args:
        df (pd.DataFrame): El DataFrame con los datos.
        terminos (str): Una cadena con los términos separados por espacios.

    Returns:
        pd.DataFrame: Un nuevo DataFrame filtrado.
    """
    terminos_lista = [termino.lower() for termino in terminos.split()]
    
    # Filtrar las filas donde todos los términos están en 'description' (ignorando mayúsculas/minúsculas)
    df_filtrado = df[df['description'].apply(
        lambda x: all(termino in x.lower() for termino in terminos_lista)
    )]
    
    return df_filtrado.reset_index(drop=True)


def al_principio_de_la_descripcion(df, termino):
    """
    Filtra las filas de un DataFrame donde el término aparece al principio de la columna 'description'.

    Args:
        df (pd.DataFrame): El DataFrame con los datos.
        termino (str): El término a buscar al principio de la columna 'description'.

    Returns:
        pd.DataFrame: Un DataFrame filtrado con las filas que cumplen la condición.
    """
    termino_lower = termino.lower()
    df_filtrado = df[df['description'].apply(lambda x: x.lower().startswith(termino_lower))]
    return df_filtrado.reset_index(drop=True)



def alguno_de_los_terminos_presentes(df, terminos):
    """
    Filtra las filas de un DataFrame donde al menos uno de los términos aparece en la columna 'description'.

    Args:
        df (pd.DataFrame): El DataFrame con los datos.
        terminos (str): Una cadena con los términos separados por espacios.

    Returns:
        pd.DataFrame: Un DataFrame filtrado con las filas que cumplen la condición.
    """
    terminos_lista = [termino.lower() for termino in terminos.split()]
    df_filtrado = df[df['description'].apply(
        lambda x: any(termino in x.lower() for termino in terminos_lista)
    )]
    return df_filtrado.reset_index(drop=True)


def alguno_de_los_terminos_presentes_al_inicio(df, terminos):
    """
    Filtra las filas de un DataFrame donde al menos uno de los términos aparece al inicio 
    de la columna 'description'.

    Args:
        df (pd.DataFrame): El DataFrame con los datos.
        terminos (str): Una cadena con los términos separados por espacios.

    Returns:
        pd.DataFrame: Un DataFrame filtrado con las filas que cumplen la condición.
    """
    terminos_lista = [termino.lower() for termino in terminos.split()]
    df_filtrado = df[df['description'].apply(
        lambda x: any(x.lower().startswith(termino) for termino in terminos_lista)
    )]
    return df_filtrado.reset_index(drop=True)


def no_esta_presente_termino(df, termino):
    """
    Filtra las filas de un DataFrame donde un término no está presente en la columna 'description'.

    Args:
        df (pd.DataFrame): El DataFrame con los datos.
        termino (str): El término a verificar si no está presente.

    Returns:
        pd.DataFrame: Un DataFrame filtrado con las filas que cumplen la condición.
    """
    termino_lower = termino.lower()
    df_filtrado = df[~df['description'].apply(lambda x: termino_lower in x.lower())]
    return df_filtrado.reset_index(drop=True)


def no_estan_presentes_terminos(df, terminos):
    """
    Filtra las filas de un DataFrame donde ninguno de los términos está presente en la columna 'description'.

    Args:
        df (pd.DataFrame): El DataFrame con los datos.
        terminos (str): Una cadena con los términos separados por espacios.

    Returns:
        pd.DataFrame: Un DataFrame filtrado con las filas que cumplen la condición.
    """
    terminos_lista = [termino.lower() for termino in terminos.split()]
    df_filtrado = df[~df['description'].apply(
        lambda x: any(termino in x.lower() for termino in terminos_lista)
    )]
    return df_filtrado.reset_index(drop=True)


def primer_termino_presente_seguientes_no_presente(df, terminos):
    """
    Filtra las filas de un DataFrame donde el primer término está presente y los siguientes términos no están presentes
    en la columna 'description'.

    Args:
        df (pd.DataFrame): El DataFrame con los datos.
        terminos (str): Una cadena con varios términos separados por espacios.

    Returns:
        pd.DataFrame: Un DataFrame filtrado con las filas que cumplen la condición.
    """
    terminos_lista = [termino.lower() for termino in terminos.split()]
    
    # El primer término debe estar presente, los siguientes no
    primer_termino = terminos_lista[0]
    siguientes_terminos = terminos_lista[1:]
    
    # Filtra las filas
    df_filtrado = df[df['description'].apply(
        lambda x: primer_termino in x.lower() and all(termino not in x.lower() for termino in siguientes_terminos)
    )]
    
    return df_filtrado.reset_index(drop=True)


def tiene_ml_l(df, terminos):
    """
    Filtra las filas de un DataFrame donde la columna 'description' contiene las unidades 'ml' o 'l' y
    verifica si la cantidad de 'ml' es mayor a 400.

    Args:
        df (pd.DataFrame): El DataFrame con los datos.

    Returns:
        pd.DataFrame: Un DataFrame filtrado con las filas que cumplen la condición.
    """
    def contiene_ml_o_l(description):
        # Busca la cantidad en 'ml' o 'l' con expresiones regulares
        match_ml = re.search(r'(\d+)\s*(ml|l)', description, re.IGNORECASE)
        if match_ml:
            cantidad = int(match_ml.group(1))
            unidad = match_ml.group(2).lower()
            # Verifica si la cantidad en ml es mayor a 400, o si la unidad es "l" (litros)
            if unidad == "ml" and cantidad > 400:
                return True
            if unidad == "l" and cantidad > 0.4:  # 1 litro = 1000 ml, por lo que 0.4 litros son 400 ml
                return True
        return False

    # Filtra el DataFrame donde la descripción cumple con el criterio
    df_filtrado = df[df['description'].apply(contiene_ml_o_l)]
    
    return df_filtrado.reset_index(drop=True)

"""
# Probar las funciones
current_dir = os.path.dirname(__file__)  # Directorio actual del script
input_dia_1 = os.path.join(current_dir, 'data', 'consolidated', '2024_12_04', 'HELADO FAMILIAR.csv')

df = pd.read_csv(input_dia_1)
terminos = "Fideos Spaghetti Tallarin"

df = tiene_ml_l(df)
#print(df)
df.to_csv("filtrado.csv", index=False)

"""