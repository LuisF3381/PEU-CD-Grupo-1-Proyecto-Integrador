import pandas as pd
import os

current_dir = os.path.dirname(__file__)  # Directorio actual del script
config_path = os.path.join(current_dir, 'base_period', 'IPC_BASE.csv')


aux = pd.read_csv(config_path)
print(aux["CLASIFICACION"])