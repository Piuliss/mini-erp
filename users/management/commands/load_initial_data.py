from django.core.management.base import BaseCommand
from django.core.management import call_command
from django.db import transaction


class Command(BaseCommand):
    help = 'Carga datos iniciales de forma segura (solo si no existen)'

    def add_arguments(self, parser):
        parser.add_argument(
            '--force',
            action='store_true',
            help='Fuerza la carga de fixtures incluso si ya existen datos',
        )

    def handle(self, *args, **options):
        from users.models import Role, User
        from inventory.models import Category

        self.stdout.write(self.style.WARNING('🔍 Verificando datos iniciales...'))

        # Verificar si ya existen datos
        roles_count = Role.objects.count()
        users_count = User.objects.count()
        categories_count = Category.objects.count()

        if not options['force'] and (roles_count > 0 or users_count > 0 or categories_count > 0):
            self.stdout.write(self.style.WARNING(
                f'⚠️  Ya existen datos en la base de datos:\n'
                f'   - Roles: {roles_count}\n'
                f'   - Usuarios: {users_count}\n'
                f'   - Categorías: {categories_count}\n'
                f'   Saltando carga de fixtures...\n'
                f'   Usa --force para cargar de todas formas (puede causar duplicados).'
            ))
            return
        
        if options['force']:
            self.stdout.write(self.style.WARNING('⚡ Modo FORCE activado - cargando fixtures...'))

        # Si no existen datos, cargar fixtures
        self.stdout.write(self.style.SUCCESS('📦 Base de datos vacía, cargando datos iniciales...'))
        
        try:
            with transaction.atomic():
                fixtures = [
                    'fixtures/roles.json',
                    'fixtures/users.json',
                    'fixtures/categories.json',
                    'fixtures/suppliers.json',
                    'fixtures/customers.json',
                    'fixtures/products.json',
                ]
                
                for fixture in fixtures:
                    try:
                        call_command('loaddata', fixture)
                        self.stdout.write(self.style.SUCCESS(f'   ✅ Cargado: {fixture}'))
                    except Exception as e:
                        self.stdout.write(self.style.WARNING(f'   ⚠️  No se pudo cargar {fixture}: {str(e)}'))
                
                self.stdout.write(self.style.SUCCESS('🎉 Datos iniciales cargados exitosamente!'))
        
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'❌ Error cargando datos: {str(e)}'))
            raise

