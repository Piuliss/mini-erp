#!/usr/bin/env python
"""
Script de backup para la base de datos PostgreSQL del Mini ERP
"""
import os
import subprocess
import argparse
from datetime import datetime
from pathlib import Path


def create_backup():
    """Crear backup de la base de datos"""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_dir = Path("backups")
    backup_dir.mkdir(exist_ok=True)
    
    backup_file = backup_dir / f"mini_erp_backup_{timestamp}.sql"
    
    print(f"🔄 Creando backup: {backup_file}")
    
    try:
        # Crear backup usando pg_dump
        cmd = f"pg_dump -h localhost -U erp_user -d mini_erp > {backup_file}"
        result = subprocess.run(cmd, shell=True, check=True, capture_output=True, text=True)
        
        print(f"✅ Backup creado exitosamente: {backup_file}")
        print(f"📊 Tamaño: {backup_file.stat().st_size / 1024:.2f} KB")
        
        return str(backup_file)
    except subprocess.CalledProcessError as e:
        print(f"❌ Error creando backup: {e}")
        if e.stderr:
            print(f"Error details: {e.stderr}")
        return None


def restore_backup(backup_file):
    """Restaurar backup de la base de datos"""
    if not Path(backup_file).exists():
        print(f"❌ Archivo de backup no encontrado: {backup_file}")
        return False
    
    print(f"🔄 Restaurando backup: {backup_file}")
    
    try:
        # Restaurar backup usando psql
        cmd = f"psql -h localhost -U erp_user -d mini_erp < {backup_file}"
        result = subprocess.run(cmd, shell=True, check=True, capture_output=True, text=True)
        
        print("✅ Backup restaurado exitosamente")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Error restaurando backup: {e}")
        if e.stderr:
            print(f"Error details: {e.stderr}")
        return False


def list_backups():
    """Listar backups disponibles"""
    backup_dir = Path("backups")
    if not backup_dir.exists():
        print("📁 No hay directorio de backups")
        return
    
    backups = list(backup_dir.glob("mini_erp_backup_*.sql"))
    
    if not backups:
        print("📁 No hay backups disponibles")
        return
    
    print("📁 Backups disponibles:")
    for backup in sorted(backups, reverse=True):
        size = backup.stat().st_size / 1024
        modified = datetime.fromtimestamp(backup.stat().st_mtime)
        print(f"  📄 {backup.name} ({size:.2f} KB) - {modified.strftime('%Y-%m-%d %H:%M:%S')}")


def main():
    parser = argparse.ArgumentParser(description="Script de backup para Mini ERP")
    parser.add_argument('action', choices=['create', 'restore', 'list'], help='Acción a realizar')
    parser.add_argument('--file', help='Archivo de backup para restaurar')
    
    args = parser.parse_args()
    
    if args.action == 'create':
        create_backup()
    elif args.action == 'restore':
        if not args.file:
            print("❌ Debes especificar un archivo de backup con --file")
            return
        restore_backup(args.file)
    elif args.action == 'list':
        list_backups()


if __name__ == '__main__':
    main()
