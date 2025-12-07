# hybrid_update_system.py - Versión mejorada con manejo de errores
import os
import sys
import json
import zipfile
import hashlib
from pathlib import Path
from datetime import datetime
import customtkinter as ctk
from tkinter import messagebox

# Intentar importar requests con manejo de errores
try:
    import requests
    REQUESTS_AVAILABLE = True
except ImportError:
    REQUESTS_AVAILABLE = False
    print("⚠️  Advertencia: El módulo 'requests' no está instalado.")
    print("   Las actualizaciones automáticas no estarán disponibles.")
    print("   Para instalar: pip install requests")

class HybridUpdateSystem:
    """Sistema híbrido de actualizaciones con manejo de errores"""
    
    def __init__(self, app_name="CalculadoraEnergia"):
        self.app_name = app_name
        self.base_url = "https://raw.githubusercontent.com/tu_usuario/tu_repo/main"
        self.update_config = self.load_update_config()
        self.modules_dir = "dynamic_modules"
        self.assets_dir = "dynamic_assets"
        
        # Crear directorios necesarios
        self.create_directories()
    
    def create_directories(self):
        """Crea los directorios necesarios"""
        directories = [self.modules_dir, self.assets_dir, "cache", "backups"]
        for directory in directories:
            Path(directory).mkdir(exist_ok=True)
    
    def load_update_config(self):
        """Carga la configuración de actualizaciones"""
        config_path = "update_config.json"
        default_config = {
            "current_version": "1.0.0",
            "update_channel": "stable",
            "auto_check": REQUESTS_AVAILABLE,  # Solo auto-check si requests está disponible
            "last_check": None,
            "installed_modules": [],
            "update_server": self.base_url,
            "requests_available": REQUESTS_AVAILABLE
        }
        
        if os.path.exists(config_path):
            try:
                with open(config_path, 'r') as f:
                    loaded = json.load(f)
                    default_config.update(loaded)
            except:
                pass
        
        return default_config
    
    def check_updates(self, force=False):
        """Verifica actualizaciones con manejo de falta de requests"""
        
        if not REQUESTS_AVAILABLE:
            return {
                "available": False,
                "error": "Módulo 'requests' no instalado",
                "instructions": "Ejecuta: pip install requests"
            }
        
        # Si no es forzado y ya verificamos hoy, usar caché
        if not force and self.update_config.get("last_check"):
            try:
                last_check = datetime.fromisoformat(self.update_config["last_check"])
                if (datetime.now() - last_check).days < 1:
                    return self.get_cached_updates()
            except:
                pass
        
        try:
            # Obtener manifest de actualizaciones
            manifest_url = f"{self.update_config['update_server']}/manifest.json"
            response = requests.get(manifest_url, timeout=10)
            response.raise_for_status()
            manifest = json.loads(response.text)
            
            # Filtrar por canal
            channel = self.update_config['update_channel']
            channel_updates = manifest.get(channel, {})
            
            # Cachear resultados
            self.cache_updates(channel_updates)
            
            # Actualizar timestamp
            self.update_config['last_check'] = datetime.now().isoformat()
            self.save_update_config()
            
            return {
                "available": bool(channel_updates.get("modules")),
                **channel_updates
            }
            
        except requests.exceptions.RequestException as e:
            print(f"Error de red al verificar updates: {e}")
            return {
                "available": False,
                "error": "Error de conexión",
                "details": str(e)
            }
        except Exception as e:
            print(f"Error checking updates: {e}")
            return {
                "available": False,
                "error": "Error inesperado",
                "details": str(e)
            }
    
    def check_updates_with_fallback(self):
        """Verifica updates con métodos alternativos si requests no está disponible"""
        
        if not REQUESTS_AVAILABLE:
            # Método alternativo: usar urllib (incluido en Python)
            return self.check_updates_with_urllib()
        
        return self.check_updates()
    
    def check_updates_with_urllib(self):
        """Verifica updates usando urllib (sin necesidad de requests)"""
        try:
            import urllib.request
            import urllib.error
            
            manifest_url = f"{self.update_config['update_server']}/manifest.json"
            
            req = urllib.request.Request(manifest_url)
            with urllib.request.urlopen(req, timeout=10) as response:
                data = response.read().decode('utf-8')
                manifest = json.loads(data)
                
                channel = self.update_config['update_channel']
                channel_updates = manifest.get(channel, {})
                
                return {
                    "available": bool(channel_updates.get("modules")),
                    **channel_updates
                }
                
        except urllib.error.URLError as e:
            return {
                "available": False,
                "error": "Error de conexión (urllib)",
                "details": str(e)
            }
        except Exception as e:
            return {
                "available": False,
                "error": "Error verificando updates",
                "details": str(e)
            }
    
    def download_module(self, module_name, version):
        """Descarga un módulo con manejo de métodos alternativos"""
        
        if not REQUESTS_AVAILABLE:
            return self.download_module_with_urllib(module_name, version)
        
        module_url = f"{self.update_config['update_server']}/modules/{module_name}_{version}.zip"
        
        try:
            # Descargar con requests
            response = requests.get(module_url, timeout=30)
            response.raise_for_status()
            
            # Guardar temporalmente
            temp_zip = f"cache/{module_name}_{version}.zip"
            with open(temp_zip, 'wb') as f:
                f.write(response.content)
            
            # Verificar hash si está disponible
            hash_url = f"{module_url}.sha256"
            try:
                hash_response = requests.get(hash_url, timeout=10)
                expected_hash = hash_response.text.strip()
                
                with open(temp_zip, 'rb') as f:
                    actual_hash = hashlib.sha256(f.read()).hexdigest()
                
                if actual_hash != expected_hash:
                    os.remove(temp_zip)
                    return False, "Verificación de hash falló"
            except:
                pass  # Si no hay hash, continuar
            
            return True, temp_zip
            
        except Exception as e:
            return False, str(e)
    
    def download_module_with_urllib(self, module_name, version):
        """Descarga usando urllib"""
        try:
            import urllib.request
            
            module_url = f"{self.update_config['update_server']}/modules/{module_name}_{version}.zip"
            temp_zip = f"cache/{module_name}_{version}.zip"
            
            urllib.request.urlretrieve(module_url, temp_zip)
            return True, temp_zip
            
        except Exception as e:
            return False, str(e)
    
    def cache_updates(self, updates):
        """Cachea los resultados de actualización"""
        cache_data = {
            "timestamp": datetime.now().isoformat(),
            "updates": updates
        }
        
        with open("cache/updates_cache.json", 'w') as f:
            json.dump(cache_data, f, indent=2)
    
    def get_cached_updates(self):
        """Obtiene updates cacheados"""
        cache_path = "cache/updates_cache.json"
        if os.path.exists(cache_path):
            try:
                with open(cache_path, 'r') as f:
                    cache_data = json.load(f)
                    return cache_data.get("updates", {})
            except:
                pass
        return {}