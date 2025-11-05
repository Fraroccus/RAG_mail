"""
Script di setup per inizializzare il database PostgreSQL
"""

import psycopg2
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT
import os
from dotenv import load_dotenv

load_dotenv()


def create_database():
    """Crea il database se non esiste"""
    
    # Connetti a PostgreSQL (database di default postgres)
    try:
        connection = psycopg2.connect(
            user=input("PostgreSQL username (default: postgres): ") or "postgres",
            password=input("PostgreSQL password: "),
            host=input("PostgreSQL host (default: localhost): ") or "localhost",
            port=input("PostgreSQL port (default: 5432): ") or "5432"
        )
        connection.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
        
        cursor = connection.cursor()
        
        # Nome database
        db_name = input("Nome database (default: email_rag_db): ") or "email_rag_db"
        
        # Controlla se il database esiste
        cursor.execute(f"SELECT 1 FROM pg_database WHERE datname = '{db_name}'")
        exists = cursor.fetchone()
        
        if exists:
            print(f"✓ Database '{db_name}' già esistente")
        else:
            # Crea database
            cursor.execute(f"CREATE DATABASE {db_name}")
            print(f"✓ Database '{db_name}' creato con successo")
        
        cursor.close()
        connection.close()
        
        return True
        
    except Exception as e:
        print(f"✗ Errore: {e}")
        return False


def create_env_file():
    """Crea file .env con configurazione"""
    
    if os.path.exists('.env'):
        overwrite = input(".env già esistente. Sovrascrivere? (s/n): ")
        if overwrite.lower() != 's':
            print("Setup annullato")
            return False
    
    print("\n" + "=" * 60)
    print("CONFIGURAZIONE MICROSOFT GRAPH API")
    print("=" * 60)
    print("Per ottenere le credenziali:")
    print("1. Vai su https://portal.azure.com")
    print("2. Azure Active Directory > App registrations > New registration")
    print("3. Configura le API permissions per Mail.Read e Mail.Send")
    print()
    
    ms_client_id = input("MS_CLIENT_ID: ")
    ms_client_secret = input("MS_CLIENT_SECRET: ")
    ms_tenant_id = input("MS_TENANT_ID: ")
    
    print("\n" + "=" * 60)
    print("CONFIGURAZIONE DATABASE")
    print("=" * 60)
    
    db_user = input("Database username (default: postgres): ") or "postgres"
    db_password = input("Database password: ")
    db_host = input("Database host (default: localhost): ") or "localhost"
    db_port = input("Database port (default: 5432): ") or "5432"
    db_name = input("Database name (default: email_rag_db): ") or "email_rag_db"
    
    database_url = f"postgresql://{db_user}:{db_password}@{db_host}:{db_port}/{db_name}"
    
    print("\n" + "=" * 60)
    print("CONFIGURAZIONE FLASK")
    print("=" * 60)
    
    import secrets
    flask_secret = secrets.token_hex(32)
    print(f"Chiave segreta generata automaticamente: {flask_secret[:20]}...")
    
    # Crea file .env
    env_content = f"""# Microsoft Graph API Configuration
MS_CLIENT_ID={ms_client_id}
MS_CLIENT_SECRET={ms_client_secret}
MS_TENANT_ID={ms_tenant_id}
MS_REDIRECT_URI=http://localhost:5000/callback

# Database Configuration
DATABASE_URL={database_url}

# Flask Configuration
FLASK_SECRET_KEY={flask_secret}

# Email Signature (Optional)
EMAIL_SIGNATURE=
"""
    
    with open('.env', 'w') as f:
        f.write(env_content)
    
    print("\n✓ File .env creato con successo")
    return True


def main():
    print("=" * 60)
    print("SETUP DATABASE - EMAIL RAG SYSTEM")
    print("=" * 60)
    print()
    
    # Step 1: Crea database
    print("STEP 1: Creazione database PostgreSQL")
    print("-" * 60)
    if not create_database():
        return
    
    print()
    
    # Step 2: Crea file .env
    print("STEP 2: Configurazione ambiente")
    print("-" * 60)
    if not create_env_file():
        return
    
    print()
    print("=" * 60)
    print("✓ SETUP COMPLETATO")
    print("=" * 60)
    print()
    print("Prossimi passi:")
    print("1. Installa le dipendenze: pip install -r requirements.txt")
    print("2. Avvia Flask: python flask_app.py")
    print("3. Il database verrà inizializzato automaticamente al primo avvio")
    print()


if __name__ == '__main__':
    main()
