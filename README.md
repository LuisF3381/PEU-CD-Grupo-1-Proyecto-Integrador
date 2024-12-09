# PEU-CD-Grupo-1-Proyecto-Integrador
Proyecto Integrador sobre Cálculo del índice de precios al consumidor utilizando datos de la web para el departamento de Lima usando las categorías establecidas en la Encuesta Nacional De Presupuestos Nacionales (ENAPREF)

## Índice
1. [Documentación](#Documentación)
2. [Comenzando](#Comenzando) 🚀
3. [Autores](#Autores) ✒️
5. [Licencia](#licencia)

![image](https://github.com/user-attachments/assets/bbae94ff-4f9f-4620-8d20-e1f10cb13828)

## Documentación
[Volver al inicio](#Índice)

La documentación del proyecto se puede encontrar en el siguiente repositorio: 
[Documentación del repositorio](../../wiki)

## Comenzando
[Volver al inicio](#Índice)

Estas instrucciones te permitirán obtener una copia del proyecto en funcionamiento en tu máquina local para propósitos de desarrollo y pruebas

### Pre-requisitos 📋
[Volver al inicio](#Índice)

- Anaconda [Descargar](https://www.anaconda.com/download)

### Instalación 🔧
[Volver al inicio](#Índice)

Para poder ejecutar los códigos, primero se tiene que crear un environment realizando los siguientes pasos:

**1. Entrar a la consola de Anaconda (Anaconda Prompt (Anaconda))**

**2. Dentro de la consola de Anaconda, crear el environment con el siguiente comando:**
```bash
conda create -n ENV_NAME python=3.12.3
```
**3. Una vez creado el environment, acceder a ella usando el siguiente comando:**
```bash
conda activate ENV_NAME
```
**4. Instalar todas las librerías necesarias en el environment haciendo uso del archivo**
[requirements.txt](PEU-CD-Grupo-1-Proyecto-Integrador/test-entorno-scraping/requirements.txt)
```bash
pip install -r requirements.txt
```
**4. Una vez finalizado todo, para desactivar el environment, ejecutar el siguiente comando:**
```bash
conda deactivate
```

### Ejecución ⚙️
[Volver al inicio](#Índice)

Para ejecutar cualquier código de extracción de datos, se debe seguir los siguientes pasos:
**1. Clonar el repositorio en una carpeta usando el comando:**
```bash
git clone https://github.com/LuisF3381/PEU-CD-Grupo-1-Proyecto-Integrador.git
```

**2. Una vez clonado el proyecto de github, dirigirse a la carpeta que contiene los códigos de los scrapers [Carpeta de los Scrapers](PEU-CD-Grupo-1-Proyecto-Integrador/ipc-webscraping):**
```bash
cd PEU-CD-Grupo-1-Proyecto-Integrador/ipc-webscraping
```
**3. Desde la consola de Anaconda, activar nuevamente el environment**
```bash
conda activate ENV_NAME
```

**4. seleccionar uno de los siguientes códigos según la página web a scrapear:**

| **Website** | **Ruta Código** |
| ----------- | ----------- |
| **Metro** | [supermarket_execution_metro.py](PEU-CD-Grupo-1-Proyecto-Integrador/ipc-webscraping/supermarket_execution_metro.py) |
| **Rappi** | [scrapers/rappi.py](PEU-CD-Grupo-1-Proyecto-Integrador/ipc-webscraping/scrapers/rappi.py) |
| **PedidosYa** | [scrapers/pedidos_ya.py](PEU-CD-Grupo-1-Proyecto-Integrador/ipc-webscraping/scrapers/pedidos_ya.py) |
| **Plaza Vea** | [supermarket_execution_plaza_vea.py](PEU-CD-Grupo-1-Proyecto-Integrador/ipc-webscraping/supermarket_execution_plaza_vea.py) |
| **Tambo** | [supermarket_execution_tambo.py](PEU-CD-Grupo-1-Proyecto-Integrador/ipc-webscraping/supermarket_execution_tambo.py) |
| **Tottus** | [supermarket_execution_tottus.py](PEU-CD-Grupo-1-Proyecto-Integrador/ipc-webscraping/supermarket_execution_tottus.py) |
| **Vega** | [supermarket_execution_vega.py](PEU-CD-Grupo-1-Proyecto-Integrador/ipc-webscraping/supermarket_execution_vega.py) |
| **Vivanda** | [supermarket_execution_vivanda.py](PEU-CD-Grupo-1-Proyecto-Integrador/ipc-webscraping/supermarket_execution_vivanda.py) |
| **Wong** | [supermarket_execution_wong.py](PEU-CD-Grupo-1-Proyecto-Integrador/ipc-webscraping/supermarket_execution_wong.py) |

**5. Una vez elegido el código a ejecutar, correr el siguiente código:** 
```bash
python RUTA_CODIGO
```

**6. Cabe aclarar que la información se guarda en la carpeta  raw [Carpeta](PEU-CD-Grupo-1-Proyecto-Integrador/ipc-webscraping/data/raw)**


## Autores ✒️
[Volver al inicio](#Índice)

* **Claudia Vivas** - *Grupo 1* - [claudiavivas](https://github.com/claudiavivas)
* **Erick Gonzales** - *Grupo 1* - [ErickEliGonzales](https://github.com/ErickEliGonzales)
* **Javier Portella** - *Grupo 1* - [JavierPortella](https://github.com/JavierPortella)
* **Luis Moquillaza** - *Grupo 1* - [LuisF3381](https://github.com/LuisF3381)
* **Oskar Quiroz** - *Grupo 1* - [Oskrabble](https://github.com/Oskrabble)