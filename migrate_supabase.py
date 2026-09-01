import os
import sys

def main():
    print("=" * 60)
    print("  Touch & Solve - Supabase Database Migrator & Seeder")
    print("=" * 60)
    
    password = input("Enter your Supabase Database Password (e.g. TouchSolve2026!): ").strip()
    if not password:
        print("Password cannot be empty.")
        return
        
    region = input("Enter your Supabase region [default: ap-southeast-1]: ").strip() or "ap-southeast-1"
    
    project_ref = "vxryghvrnoltiotktmoa"
    db_url = f"postgresql://postgres.{project_ref}:{password}@aws-0-{region}.pooler.supabase.com:6543/postgres?sslmode=require"
    
    os.environ['DATABASE_URL'] = db_url
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'tns_microfinance.settings')
    
    import django
    django.setup()
    
    from django.core.management import call_command
    print(f"\n[1/2] Connecting & running migrations to Supabase ({region})...")
    call_command('migrate', interactive=False)
    
    print("\n[2/2] Seeding initial data to Supabase...")
    import seed_data
    
    print("\n" + "=" * 60)
    print("  [SUCCESS] All tables and demo users created on Supabase!")
    print("=" * 60)
    print(f"\nCopy this DATABASE_URL into Vercel Settings -> Environment Variables:\n")
    print(db_url)
    print("\n" + "=" * 60)

if __name__ == '__main__':
    main()
