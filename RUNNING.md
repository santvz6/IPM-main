# RUNNING.md

La aplicación cuenta con dos formas distintas de juego. Para la primera de ellas, la más simple, no será necesario utilizar conda ni mediapipe; para la segunda, deberemos crear un segundo entorno virtual e instalar las correspondientes dependencias


# 1. Creación del entorno

## 1.1 Entorno del juego

```bash
python -m venv venv
source venv/bin/activate   # Linux / Mac
venv\Scripts\activate      # Windows
```

```bash
pip install -r app/requirements.txt
```

## 1.2 Entorno de mediapipe (extra)

#### 1.2.1 Prerrequisitos (mediapipe)

- Tener instalado **Conda**:  
  [Descargar Conda](https://docs.conda.io/en/latest/miniconda.html)  
- Tener Python 3.12 disponible.  
- Tener una cámara conectada y funcionando.


## 1.2.2 Creación del entorno

```bash
conda create -n IPM python=3.12
conda activate IPM
```

```bash
pip install -r mediapipe/requirements.txt
```

```bash
python mediapipe/
download_models.py
```


## 2. Ejecución

## 2.1 Ejecución del juego

```bash
python app/main.py
```
## 2.2 Ejecución de mediapipe

```bash
python mediapipe/main.py
```