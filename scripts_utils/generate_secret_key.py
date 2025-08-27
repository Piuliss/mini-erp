#!/usr/bin/env python
"""
Script para generar SECRET_KEYs seguros para Django
"""
import secrets
import string
import argparse


def generate_secret_key(length=50):
    """
    Genera un SECRET_KEY seguro para Django
    
    Args:
        length (int): Longitud del SECRET_KEY (default: 50)
    
    Returns:
        str: SECRET_KEY generado
    """
    # Caracteres permitidos para el SECRET_KEY
    alphabet = string.ascii_letters + string.digits + '!@#$%^&*(-_=+)'
    
    # Generar SECRET_KEY aleatorio
    secret_key = ''.join(secrets.choice(alphabet) for _ in range(length))
    
    return secret_key


def generate_django_secret_key():
    """
    Genera un SECRET_KEY específicamente para Django
    Usa el mismo formato que django.core.management.utils.get_random_secret_key()
    """
    # Caracteres específicos para Django SECRET_KEY
    chars = 'abcdefghijklmnopqrstuvwxyz0123456789!@#$%^&*(-_=+)'
    
    # Generar 50 caracteres aleatorios
    return ''.join(secrets.choice(chars) for _ in range(50))


def main():
    parser = argparse.ArgumentParser(description="Generar SECRET_KEYs seguros para Django")
    parser.add_argument(
        '--length', 
        type=int, 
        default=50, 
        help='Longitud del SECRET_KEY (default: 50)'
    )
    parser.add_argument(
        '--django-format', 
        action='store_true', 
        help='Usar formato específico de Django'
    )
    parser.add_argument(
        '--env-file', 
        action='store_true', 
        help='Generar formato para archivo .env'
    )
    parser.add_argument(
        '--settings-file', 
        action='store_true', 
        help='Generar formato para settings.py'
    )
    
    args = parser.parse_args()
    
    if args.django_format:
        secret_key = generate_django_secret_key()
    else:
        secret_key = generate_secret_key(args.length)
    
    print("🔐 SECRET_KEY generado:")
    print()
    
    if args.env_file:
        print("Para archivo .env:")
        print(f"SECRET_KEY={secret_key}")
    elif args.settings_file:
        print("Para settings.py:")
        print(f"SECRET_KEY = '{secret_key}'")
    else:
        print(secret_key)
    
    print()
    print("⚠️  IMPORTANTE:")
    print("   - Guarda este SECRET_KEY en un lugar seguro")
    print("   - Nunca lo compartas o subas a control de versiones")
    print("   - Usa diferentes SECRET_KEYs para desarrollo y producción")
    print("   - Para producción, considera usar variables de entorno")


if __name__ == '__main__':
    main()
