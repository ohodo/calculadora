# build_with_requests.py
import PyInstaller.__main__
import os
import subprocess
import sys

def install_requirements():
    """Instala los requerimientos"""
    print("📦 Instalando dependencias...")
    
    requirements = [
        "requests==2.31.0",
        "customtkinter==5.2.2",
        "pillow==10.1.0"
    ]
    
    for req in requirements:
        try:
            subprocess.check_call([sys.executable, "-m", "pip", "install", req])
            print(f"✅ {req}")
        except:
            print(f"❌ Error instalando {req}")
    
    print("✅ Dependencias instaladas")

def compile_app():
    """Compila la aplicación incluyendo requests"""
    
    # Asegurar que requests está instalado
    try:
        import requests
        print(f"✅ requests {requests.__version__} está instalado")
    except ImportError:
        print("❌ requests no está instalado, instalando...")
        install_requirements()
    
    # Comando de compilación
    args = [
        "calc.py",  # Tu archivo principal
        "--onefile",
        "--windowed",
        "--name=CalculadoraEnergia",
        "--icon=icon.ico" if os.path.exists("icon.ico") else "",
        "--add-data=maq.db;.",
        "--hidden-import=customtkinter",
        "--hidden-import=PIL",
        "--hidden-import=requests",
        "--hidden-import=urllib3",
        "--hidden-import=chardet",
        "--hidden-import=idna",
        "--collect-all=requests",  # IMPORTANTE: incluir todo requests
        "--clean",
        "--noconfirm"
    ]
    
    # Filtrar elementos vacíos
    args = [arg for arg in args if arg]
    
    print("🔨 Compilando aplicación...")
    PyInstaller.__main__.run(args)

if __name__ == "__main__":
    compile_app()