#!/usr/bin/env python3
"""
Script para automatizar la generación de tags de versiones
"""
import subprocess
import sys
import re
from datetime import datetime
import argparse


def run_command(command):
    """Ejecutar comando y retornar output"""
    try:
        result = subprocess.run(command, shell=True, capture_output=True, text=True, check=True)
        return result.stdout.strip()
    except subprocess.CalledProcessError as e:
        print(f"❌ Error ejecutando comando: {command}")
        print(f"Error: {e.stderr}")
        return None


def get_current_version():
    """Obtener la versión actual del proyecto"""
    # Intentar obtener desde VERSION (prioridad más alta)
    try:
        with open('VERSION', 'r') as f:
            version = f.read().strip()
            if version:
                return version
    except FileNotFoundError:
        pass
    
    # Intentar obtener desde setup.py
    try:
        with open('setup.py', 'r') as f:
            content = f.read()
            match = re.search(r"version=['\"]([^'\"]+)['\"]", content)
            if match:
                return match.group(1)
    except FileNotFoundError:
        pass
    
    # Intentar obtener desde pyproject.toml
    try:
        with open('pyproject.toml', 'r') as f:
            content = f.read()
            match = re.search(r'version = "([^"]+)"', content)
            if match:
                return match.group(1)
    except FileNotFoundError:
        pass
    
    # Si no encuentra archivo de configuración, usar versión por defecto
    return "0.1.0"


def get_latest_tag():
    """Obtener el último tag de git"""
    result = run_command("git describe --tags --abbrev=0 2>/dev/null || echo 'v0.0.0'")
    return result if result else "v0.0.0"


def parse_version(version_string):
    """Parsear versión en formato semver"""
    # Remover 'v' si existe
    version_string = version_string.lstrip('v')
    
    # Separar en componentes
    parts = version_string.split('.')
    major = int(parts[0]) if len(parts) > 0 else 0
    minor = int(parts[1]) if len(parts) > 1 else 0
    patch = int(parts[2]) if len(parts) > 2 else 0
    
    return major, minor, patch


def increment_version(version_string, increment_type):
    """Incrementar versión según el tipo especificado"""
    major, minor, patch = parse_version(version_string)
    
    if increment_type == 'major':
        major += 1
        minor = 0
        patch = 0
    elif increment_type == 'minor':
        minor += 1
        patch = 0
    elif increment_type == 'patch':
        patch += 1
    else:
        raise ValueError(f"Tipo de incremento inválido: {increment_type}")
    
    return f"v{major}.{minor}.{patch}"


def generate_changelog(previous_tag, new_tag):
    """Generar changelog entre tags"""
    if previous_tag == "v0.0.0":
        # Si es el primer tag, obtener todos los commits
        commits = run_command(f"git log --oneline --no-merges")
    else:
        # Obtener commits entre tags
        commits = run_command(f"git log {previous_tag}..HEAD --oneline --no-merges")
    
    if not commits:
        return "No hay cambios significativos"
    
    # Filtrar commits de merge y formatear
    commit_lines = commits.split('\n')
    filtered_commits = []
    
    for commit in commit_lines:
        if commit and not commit.startswith('Merge'):
            # Extraer mensaje del commit
            message = commit.split(' ', 1)[1] if ' ' in commit else commit
            filtered_commits.append(f"- {message}")
    
    return '\n'.join(filtered_commits)


def update_version_file(version):
    """Actualizar archivo VERSION con la nueva versión"""
    try:
        with open('VERSION', 'w') as f:
            f.write(version.lstrip('v') + '\n')
        print(f"📝 Archivo VERSION actualizado a {version.lstrip('v')}")
        return True
    except Exception as e:
        print(f"⚠️  No se pudo actualizar archivo VERSION: {e}")
        return False

def create_tag(version, message=None, push=True):
    """Crear tag en git"""
    if not message:
        message = f"Release {version}"
    
    # Verificar que no hay cambios sin commitear
    status = run_command("git status --porcelain")
    if status:
        print("⚠️  Hay cambios sin commitear:")
        print(status)
        response = input("¿Deseas continuar? (y/N): ")
        if response.lower() != 'y':
            print("❌ Operación cancelada")
            return False
    
    # Actualizar archivo VERSION
    update_version_file(version)
    
    # Commit del archivo VERSION si hay cambios
    if run_command("git status --porcelain | grep VERSION"):
        run_command(f'git add VERSION && git commit -m "Update version to {version.lstrip("v")}"')
    
    # Crear tag
    print(f"🏷️  Creando tag: {version}")
    tag_command = f'git tag -a {version} -m "{message}"'
    if not run_command(tag_command):
        print("❌ Error creando tag")
        return False
    
    # Push del tag si se solicita
    if push:
        print(f"🚀 Haciendo push del tag: {version}")
        push_command = f"git push origin {version}"
        if not run_command(push_command):
            print("❌ Error haciendo push del tag")
            return False
    
    print(f"✅ Tag {version} creado exitosamente")
    return True


def main():
    parser = argparse.ArgumentParser(description='Generar tags de versión automáticamente')
    parser.add_argument('--type', '-t', 
                       choices=['major', 'minor', 'patch'],
                       default='patch',
                       help='Tipo de incremento de versión (default: patch)')
    parser.add_argument('--message', '-m',
                       help='Mensaje personalizado para el tag')
    parser.add_argument('--no-push', '-n',
                       action='store_true',
                       help='No hacer push del tag automáticamente')
    parser.add_argument('--current', '-c',
                       action='store_true',
                       help='Mostrar versión actual')
    parser.add_argument('--list', '-l',
                       action='store_true',
                       help='Listar todos los tags')
    parser.add_argument('--changelog', '-g',
                       action='store_true',
                       help='Generar changelog para la nueva versión')
    
    args = parser.parse_args()
    
    # Verificar que estamos en un repositorio git
    if not run_command("git rev-parse --git-dir"):
        print("❌ No estás en un repositorio git")
        sys.exit(1)
    
    if args.current:
        current = get_current_version()
        print(f"📋 Versión actual: {current}")
        return
    
    if args.list:
        tags = run_command("git tag --sort=-version:refname")
        if tags:
            print("🏷️  Tags disponibles:")
            for tag in tags.split('\n'):
                print(f"  {tag}")
        else:
            print("📭 No hay tags disponibles")
        return
    
    # Obtener versión actual y último tag
    current_version = get_current_version()
    latest_tag = get_latest_tag()
    
    print(f"📋 Versión actual: {current_version}")
    print(f"🏷️  Último tag: {latest_tag}")
    
    # Generar nueva versión
    new_version = increment_version(latest_tag, args.type)
    print(f"🆕 Nueva versión: {new_version}")
    
    # Generar changelog si se solicita
    if args.changelog:
        print("\n📝 Changelog:")
        changelog = generate_changelog(latest_tag, new_version)
        print(changelog)
        print()
    
    # Confirmar creación del tag
    if not args.message:
        message = f"Release {new_version}"
    else:
        message = args.message
    
    print(f"📝 Mensaje del tag: {message}")
    
    response = input(f"¿Crear tag {new_version}? (y/N): ")
    if response.lower() != 'y':
        print("❌ Operación cancelada")
        return
    
    # Crear tag
    success = create_tag(new_version, message, not args.no_push)
    
    if success:
        print(f"\n🎉 Tag {new_version} creado exitosamente!")
        print(f"📅 Fecha: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        
        if not args.no_push:
            print("🚀 El tag ha sido enviado a GitHub")
            print("⚡ GitHub Actions iniciará automáticamente el build y push a Docker Hub")
        else:
            print("💡 Para hacer push manualmente: git push origin {new_version}")


if __name__ == "__main__":
    main()
