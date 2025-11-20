#!/usr/bin/env python
"""
Script para configurar o banco de dados do NBA Fantasy Game
Execute: python setup_db.py
"""
import os
import sys
import django

# Configure Django settings
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'nba_fantasy.settings')
django.setup()

from django.core.management import call_command
from django.db import connection

def setup_database():
    """Configure database from scratch"""
    print("🏀 NBA Fantasy Game - Database Setup")
    print("=" * 50)
    print()

    # Check if database exists
    try:
        with connection.cursor() as cursor:
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
            tables = cursor.fetchall()
            if tables:
                print(f"⚠️  Found {len(tables)} existing tables")
                response = input("Do you want to delete and recreate the database? (y/n): ")
                if response.lower() != 'y':
                    print("Aborted.")
                    return

                # Delete database file
                if os.path.exists('db.sqlite3'):
                    os.remove('db.sqlite3')
                    print("✅ Database deleted")
    except:
        pass

    print()
    print("📊 Running migrations...")
    try:
        call_command('migrate', verbosity=1)
        print("✅ Migrations completed successfully")
    except Exception as e:
        print(f"❌ Migration failed: {e}")
        return

    print()
    print("👥 Loading player fixtures...")
    try:
        call_command('loaddata', 'players', verbosity=1)
        print("✅ Fixtures loaded successfully (25 NBA players)")
    except Exception as e:
        print(f"❌ Failed to load fixtures: {e}")
        return

    print()
    print("=" * 50)
    print("✅ Database setup completed successfully!")
    print()
    print("📚 Next steps:")
    print("   1. Create a superuser: python manage.py createsuperuser")
    print("   2. Start the server: python manage.py runserver 8000")
    print("   3. Access Swagger: http://localhost:8000/swagger/")
    print()

if __name__ == '__main__':
    setup_database()
