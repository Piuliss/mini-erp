#!/usr/bin/env python
"""
Script de gestión para desarrollo del Mini ERP
"""
import os
import sys
import subprocess
import argparse
import secrets
import string
from pathlib import Path


def generate_secret_key():
    """Genera un SECRET_KEY seguro para Django"""
    chars = 'abcdefghijklmnopqrstuvwxyz0123456789!@#$%^&*(-_=+)'
    return ''.join(secrets.choice(chars) for _ in range(50))


def run_command(command, description=""):
    """Ejecutar comando y mostrar resultado"""
    print(f"\n🔄 {description}")
    print(f"Comando: {command}")
    
    try:
        result = subprocess.run(command, shell=True, check=True, capture_output=True, text=True)
        if result.stdout:
            print("✅ Éxito:")
            print(result.stdout)
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Error: {e}")
        if e.stderr:
            print(f"Error details: {e.stderr}")
        return False


def setup_environment():
    """Configurar entorno de desarrollo"""
    print("🚀 Configurando entorno de desarrollo...")
    
    # Crear archivo .env si no existe
    env_file = Path(".env")
    if not env_file.exists():
        secret_key = generate_secret_key()
        env_content = f"""SECRET_KEY={secret_key}
DEBUG=True
DB_NAME=mini_erp
DB_USER=erp_user
DB_PASSWORD=erp_password
DB_HOST=localhost
DB_PORT=5432
USE_POSTGRES=True
"""
        with open(env_file, 'w') as f:
            f.write(env_content)
        print("✅ Archivo .env creado con SECRET_KEY aleatorio")
    
    # Configurar PostgreSQL
    setup_postgres()
    
    # Instalar dependencias
    if not run_command("pip install -r requirements.txt", "Instalando dependencias"):
        return False
    
    # Ejecutar migraciones
    if not run_command("python manage.py migrate", "Ejecutando migraciones"):
        return False
    
    # Cargar datos de prueba
    if not run_command("python manage.py loaddata fixtures/*.json", "Cargando datos de prueba"):
        return False
    
    print("\n✅ Entorno configurado correctamente!")
    return True


def create_superuser():
    """Crear superusuario"""
    print("👤 Creando superusuario...")
    
    # Verificar si ya existe un superusuario
    try:
        result = subprocess.run(
            "python manage.py shell -c \"from users.models import User; print(User.objects.filter(is_superuser=True).count())\"",
            shell=True, capture_output=True, text=True
        )
        if result.stdout.strip() == "0":
            print("No hay superusuarios. Creando uno nuevo...")
            run_command("python manage.py createsuperuser", "Creando superusuario")
        else:
            print("Ya existe un superusuario.")
    except:
        print("Error verificando superusuarios existentes.")


def run_tests():
    """Ejecutar tests"""
    print("🧪 Ejecutando tests...")
    run_command("python manage.py test", "Ejecutando tests")


def run_server():
    """Ejecutar servidor de desarrollo"""
    print("🌐 Iniciando servidor de desarrollo...")
    print("📖 Documentación disponible en:")
    print("   - Swagger UI: http://localhost:8000/api/docs/")
    print("   - ReDoc: http://localhost:8000/api/redoc/")
    print("   - Admin: http://localhost:8000/admin/")
    print("\n👥 Usuarios de prueba:")
    print("   - admin@minierp.com / test123456")
    print("   - manager@minierp.com / test123456")
    print("   - sales@minierp.com / test123456")
    print("\n⏹️  Presiona Ctrl+C para detener el servidor")
    
    run_command("python manage.py runserver", "Iniciando servidor")


def docker_setup():
    """Configurar con Docker"""
    print("🐳 Configurando con Docker...")
    
    if not run_command("docker-compose build", "Construyendo imágenes Docker"):
        return False
    
    if not run_command("docker-compose up -d", "Iniciando contenedores"):
        return False
    
    print("\n✅ Docker configurado correctamente!")
    print("📖 Servicios disponibles:")
    print("   - API: http://localhost:8000")
    print("   - Swagger: http://localhost:8000/api/docs/")
    print("   - ReDoc: http://localhost:8000/api/redoc/")
    print("   - Admin: http://localhost:8000/admin/")
    return True


def docker_stop():
    """Detener contenedores Docker"""
    print("🛑 Deteniendo contenedores Docker...")
    run_command("docker-compose down", "Deteniendo contenedores")


def setup_postgres():
    """Configurar PostgreSQL"""
    print("🐘 Configurando PostgreSQL...")
    
    # Verificar si PostgreSQL está disponible
    try:
        subprocess.run("psql --version", shell=True, capture_output=True, check=True)
        print("✅ PostgreSQL disponible")
    except:
        print("❌ PostgreSQL no disponible")
        return False
    
    # Crear usuario y base de datos
    commands = [
        "psql postgres -c \"CREATE USER erp_user WITH PASSWORD 'erp_password';\"",
        "psql postgres -c \"CREATE DATABASE mini_erp OWNER erp_user;\"",
        "psql postgres -c \"GRANT ALL PRIVILEGES ON DATABASE mini_erp TO erp_user;\""
    ]
    
    for cmd in commands:
        if not run_command(cmd, "Configurando base de datos"):
            print("⚠️  Comando falló, pero puede que ya exista la configuración")
    
    print("✅ PostgreSQL configurado")
    return True


def show_status():
    """Mostrar estado del proyecto"""
    print("📊 Estado del proyecto:")
    
    # Verificar archivos importantes
    files_to_check = [
        "requirements.txt",
        "manage.py",
        "mini_erp/settings.py",
        ".env"
    ]
    
    for file in files_to_check:
        if Path(file).exists():
            print(f"✅ {file}")
        else:
            print(f"❌ {file} (faltante)")
    
    # Verificar si Docker está disponible
    try:
        subprocess.run("docker --version", shell=True, capture_output=True, check=True)
        print("✅ Docker disponible")
    except:
        print("❌ Docker no disponible")
    
    # Verificar si PostgreSQL está disponible
    try:
        subprocess.run("psql --version", shell=True, capture_output=True, check=True)
        print("✅ PostgreSQL disponible")
    except:
        print("❌ PostgreSQL no disponible")
    
    # Verificar si Python está disponible
    try:
        result = subprocess.run("python --version", shell=True, capture_output=True, text=True)
        print(f"✅ {result.stdout.strip()}")
    except:
        print("❌ Python no disponible")
    
    # Verificar conexión a la base de datos
    try:
        result = subprocess.run(
            "python manage.py shell -c \"from django.db import connection; print('DB:', connection.settings_dict['NAME'])\"",
            shell=True, capture_output=True, text=True
        )
        if "DB: mini_erp" in result.stdout:
            print("✅ Conexión a PostgreSQL exitosa")
        else:
            print("❌ Error de conexión a PostgreSQL")
    except:
        print("❌ No se pudo verificar la conexión a PostgreSQL")


def generate_secret_key_command():
    """Generar y mostrar un SECRET_KEY seguro"""
    secret_key = generate_secret_key()
    print("🔐 SECRET_KEY generado:")
    print()
    print(f"SECRET_KEY={secret_key}")
    print()
    print("⚠️  IMPORTANTE:")
    print("   - Guarda este SECRET_KEY en un lugar seguro")
    print("   - Nunca lo compartas o subas a control de versiones")
    print("   - Usa diferentes SECRET_KEYs para desarrollo y producción")


def main():
    parser = argparse.ArgumentParser(description="Script de gestión para Mini ERP")
    parser.add_argument('command', choices=[
        'setup', 'superuser', 'test', 'run', 'docker-setup', 'docker-stop', 'status', 'postgres', 'secret-key'
    ], help='Comando a ejecutar')
    
    args = parser.parse_args()
    
    if args.command == 'setup':
        setup_environment()
    elif args.command == 'superuser':
        create_superuser()
    elif args.command == 'test':
        run_tests()
    elif args.command == 'run':
        run_server()
    elif args.command == 'docker-setup':
        docker_setup()
    elif args.command == 'docker-stop':
        docker_stop()
    elif args.command == 'status':
        show_status()
    elif args.command == 'postgres':
        setup_postgres()
    elif args.command == 'secret-key':
        generate_secret_key_command()


if __name__ == '__main__':
    main()
