import os
import json
import subprocess
import shutil
from pathlib import Path
from icoextract import IconExtractor

ARCHIVO_CONFIG = "config.json"

def cargar_config():
    if os.path.exists(ARCHIVO_CONFIG):
        try:
            with open(ARCHIVO_CONFIG, "r", encoding="utf-8") as f:
                return json.load(f)
        except: pass
    return {"bibliotecas": {}, "favoritos": []}

def guardar_config(datos):
    with open(ARCHIVO_CONFIG, "w", encoding="utf-8") as f:
        json.dump(datos, f, indent=4)

def buscar_juegos(carpeta_maestra):
    juegos_encontrados = []
    ruta = Path(carpeta_maestra)
    if not ruta.exists(): return [] 
    
    for elemento in ruta.iterdir():
        if elemento.is_dir():
            exes = list(elemento.glob('*.exe'))
            exe_p = next((e for e in exes if "unins" not in e.name.lower()), None)
            
            if exe_p:
                img_path = None
                # 1. Buscamos primero si hay una portada asignada
                for n in ["portada.png", "portada.jpg", "icon.png"]:
                    if (elemento / n).exists():
                        img_path = str(elemento / n)
                        break
                
                # 2. Si no hay, intentamos sacar el icono del EXE
                if not img_path:
                    try:
                        icon_tmp = elemento / "temp_icon.png"
                        extractor = IconExtractor(str(exe_p))
                        extractor.export_icon(str(icon_tmp))
                        img_path = str(icon_tmp)
                    except:
                        img_path = None # Dejamos en None para que la Interfaz ponga la predeterminada

                juegos_encontrados.append({
                    "nombre": elemento.name,
                    "ruta_exe": str(exe_p),
                    "ruta_carpeta": str(elemento),
                    "imagen": img_path
                })
    return juegos_encontrados

def lanzar_juego(exe, carpeta):
    subprocess.Popen([exe], cwd=carpeta)

def abrir_carpeta(ruta):
    os.startfile(ruta)

def asignar_portada_personalizada(ruta_imagen_origen, ruta_carpeta_juego):
    """Copia la imagen elegida a la carpeta del juego como 'portada.png'"""
    destino = os.path.join(ruta_carpeta_juego, "portada.png")
    shutil.copy(ruta_imagen_origen, destino)