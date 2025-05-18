import os
import django
import time

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'smooth_airlines.settings')
django.setup()

from django.db import connection

def test_connection():
    try:
        with connection.cursor() as cursor:
            cursor.execute('SELECT 1')
            result = cursor.fetchone()
            print("✅ Database connection successful!")
            print(f"Result: {result[0]}")
    except Exception as e:
        print("❌ Database connection failed!")
        print(f"Error: {str(e)}")

if __name__ == '__main__':
    print("Testing database connection...")
    start_time = time.time()
    test_connection()
    end_time = time.time()
    print(f"Connection test took {end_time - start_time:.2f} seconds") 