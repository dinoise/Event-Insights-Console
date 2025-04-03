# API Ingesta

Este proyecto es una API desarrollada en Flask.

Este archivo README proporciona instrucciones detalladas para la configuración del entorno de desarrollo y una guía completa de uso.

---

## Contenido

1. [Requisitos Previos](#requisitos-previos)
2. [Instalación del Entorno Virtual](#instalación-del-entorno-virtual)
3. [Estructura del Proyecto](#estructura-del-proyecto)
4. [Configuración](#configuración)
5. [Ejecución](#ejecución)

---

## Requisitos Previos

Antes de comenzar, asegúrate de tener instalado:

- Python 3.8+
- Pip (administrador de paquetes de Python)
- Git

## Instalación del Entorno Virtual
Un entorno virtual en Python es una carpeta aislada que contiene una instalación específica de Python y todas las dependencias necesarias para ejecutar un proyecto. Usar entornos virtuales permite que cada proyecto tenga sus propias dependencias, versiones de librerías y configuraciones, sin interferir con otros proyectos en la misma máquina. Esto ayuda a mantener el entorno de trabajo ordenado y evita conflictos de versión entre dependencias.

Para configurar el entorno de desarrollo, sigue estos pasos:

1. **Clona el repositorio del proyecto**:
   ```bash
   git clone https://github.com/est-52/delivernow_events.git
   cd delivernow_events
    ```

2. **Crea un entorno virtual**:
    ```bash
    python3 -m venv venv
    ```
    Puedes colocarle otro nombre al entorno, pero asegurate de colocar el nombre en el archivo `.gitignore`, si no, todo el entorno se subirá al repositorio, lo cual es inncesario. Ejemplo de creacion de un entorno con otro nombre:
    
    ```bash
    python3 -m venv venvPersonalizado
    ```

    ```bash
    # .gitignore
    venvPersonalizado/ # Colocando el entorno virtual en el archivo .gitignore
    ```

3. **Activar el entorno virtual**:
    - En Linux/Mac:
    ```bash
    source venv/bin/activate
    ```

    - En Windows:
    ```bash
    .\venv\Scripts\activate
    ```

4. **Instala las dependencias**:
    ```bash
    pip install -r requirements.txt
    ```

## Estructura del Proyecto
- README.md: Documentación del proyecto.
- requirements.txt: Lista de dependencias necesarias.
- .dockerfile: Archivo donde se colocan los archivos y carpetas que no se subirán a la imagen de Docker.
- Dockerfile: Archivo Docker para construir la imagen que se subirá a Google Cloud.

- .github/: Contiene el archivo de deploy a Google Cloud para github actions.

- app/: Contiene la lógica principal de la aplicación.
    - routes/: Rutas de la API.
    - controllers: Controladores para las rutas.
    - services/: Lógica de negocio para la app.
    - utils/: Funciones de utilería.
    - \_\_init\_\_.py: Inicializa la aplicación de Flask.
    - config.py: Archivo de configuración de variables de PROD y DEV.
    - main.py: Archivo principal de la app.

## Configuración
Para ejecutar este proyecto de manera local, es necesario autenticarse con Google Cloud CLI e inicializar el nombre del proyecto como una variable de entorno en el entorno virtual.

1. **Autenticación con Google Cloud**:
    
    Asegúrate de que tu cuenta de Google tenga permisos adecuados en la consola de Google Cloud. Luego, ejecuta el siguiente comando para autenticarte. Esto abrirá una página donde deberás iniciar sesión con tu cuenta:
   ```bash
   gcloud auth application-default login
    ```

2. **Inicialización de la variable de entorno del proyecto**:
    
    Especifica el proyecto en el que trabajarás estableciendo el nombre como una variable de entorno. Activa tu entorno virtual y ejecuta uno de los siguientes comandos según tu sistema operativo:

    - En Linux/Mac:
    ```bash
    export GOOGLE_CLOUD_PROJECT="e52-poc"
    ```

    - En Windows:
    ```bash
    $Env:GOOGLE_CLOUD_PROJECT="e52-poc"
    ```
    ### Nota adicional.
    También se podría configurar el entorno de desarrollo colocando la variable `FLASK_ENV` con el valor `dev`, pero esta se coloca automáticamente.

## Ejecución
Para iniciar el servidor de desarrollo (con el entorno virtual activo):
- En Linux/Mac:
```bash
python app/main.py
```

- En Windows:
```bash
python .\app\main.py
```

