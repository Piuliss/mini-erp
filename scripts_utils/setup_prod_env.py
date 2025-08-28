#!/usr/bin/env python
"""
Script para configurar el archivo .env.prod con valores seguros
"""
import os
import secrets
import string
import subprocess
import sys
from pathlib import Path


def generate_secure_password(length=16):
    """
    Genera una contraseña segura para la base de datos
    
    Args:
        length (int): Longitud de la contraseña (default: 16)
    
    Returns:
        str: Contraseña generada
    """
    # Caracteres para la contraseña (sin caracteres problemáticos)
    alphabet = string.ascii_letters + string.digits + '!@#$%'
    
    # Generar contraseña aleatoria
    password = ''.join(secrets.choice(alphabet) for _ in range(length))
    
    return password


def generate_django_secret_key():
    """
    Genera un SECRET_KEY específicamente para Django
    Evita caracteres problemáticos para bash
    """
    # Caracteres específicos para Django SECRET_KEY (sin caracteres problemáticos para bash)
    chars = 'abcdefghijklmnopqrstuvwxyz0123456789!@#$%^&*-_=+'
    
    # Generar 50 caracteres aleatorios
    return ''.join(secrets.choice(chars) for _ in range(50))


def setup_prod_env():
    """
    Configura el archivo .env.prod con valores seguros
    """
    # Rutas de archivos
    project_root = Path(__file__).parent.parent
    env_prod_path = project_root / '.env.prod'
    env_prod_example_path = project_root / 'env.prod.example'
    
    # Verificar si ya existe .env.prod
    if env_prod_path.exists():
        print("⚠️  El archivo .env.prod ya existe.")
        response = input("¿Deseas sobrescribirlo? (y/N): ").strip().lower()
        if response != 'y':
            print("❌ Operación cancelada.")
            return False
    
    # Generar valores seguros
    print("🔐 Generando valores seguros...")
    db_password = generate_secure_password()
    secret_key = generate_django_secret_key()
    
    # Leer el archivo de ejemplo
    if not env_prod_example_path.exists():
        print("❌ Error: No se encontró el archivo env.prod.example")
        return False
    
    with open(env_prod_example_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Reemplazar valores
    content = content.replace('your_secure_password', db_password)
    content = content.replace('your-production-secret-key-here', secret_key)
    
    # Generar DATABASE_URL con encoding seguro
    import urllib.parse
    safe_password = urllib.parse.quote(db_password, safe='')
    database_url = f"postgresql://minierp_user:{safe_password}@db:5432/minierp_prod"
    content = content.replace('postgresql://minierp_user:your_secure_password@db:5432/minierp_prod', database_url)
    
    # Escribir el archivo .env.prod
    with open(env_prod_path, 'w', encoding='utf-8') as f:
        f.write(content)
    
    print("✅ Archivo .env.prod creado exitosamente!")
    print()
    print("📋 Valores generados:")
    print(f"   DB_PASSWORD: {db_password}")
    print(f"   SECRET_KEY: {secret_key[:20]}...")
    print()
    print("⚠️  IMPORTANTE:")
    print("   - Guarda estos valores en un lugar seguro")
    print("   - Nunca subas el archivo .env.prod a control de versiones")
    print("   - Actualiza ALLOWED_HOSTS y CORS_ALLOWED_ORIGINS con tu dominio real")
    
    return True


def main():
    """
    Función principal
    """
    print("🚀 Configurando archivo .env.prod para producción")
    print("=" * 50)
    
    try:
        success = setup_prod_env()
        if success:
            print()
            print("🎉 Configuración completada!")
            print("   Ahora puedes ejecutar: docker-compose -f docker-compose.prod.yml up -d")
        else:
            sys.exit(1)
    except KeyboardInterrupt:
        print("\n❌ Operación cancelada por el usuario.")
        sys.exit(1)
    except Exception as e:
        print(f"❌ Error: {e}")
        sys.exit(1)


if __name__ == '__main__':
    main()
