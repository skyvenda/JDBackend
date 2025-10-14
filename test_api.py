#!/usr/bin/env python3
"""
Script de teste básico para a API Jornal Destaque
"""
import requests
import json
from datetime import datetime

# Configurações
BASE_URL = "http://localhost:8000"

def test_health():
    """Testa se a API está funcionando"""
    try:
        response = requests.get(f"{BASE_URL}/health")
        if response.status_code == 200:
            print("✅ API está funcionando")
            return True
        else:
            print(f"❌ API retornou status {response.status_code}")
            return False
    except requests.exceptions.ConnectionError:
        print("❌ Não foi possível conectar à API")
        return False

def create_admin():
    """Cria um usuário admin"""
    admin_data = {
        "nome": "Admin Jornal",
        "telefone": "11999999999",
        "email": "admin@jornaldestaque.com",
        "senha": "admin123"
    }
    
    try:
        response = requests.post(f"{BASE_URL}/admin/create-admin", json=admin_data)
        if response.status_code == 200:
            print("✅ Admin criado com sucesso")
            return response.json()
        else:
            print(f"❌ Erro ao criar admin: {response.status_code}")
            print(response.text)
            return None
    except Exception as e:
        print(f"❌ Erro ao criar admin: {e}")
        return None

def login_admin():
    """Faz login como admin"""
    login_data = {
        "email": "admin@jornaldestaque.com",
        "senha": "admin123"
    }
    
    try:
        response = requests.post(f"{BASE_URL}/user/login", json=login_data)
        if response.status_code == 200:
            print("✅ Login realizado com sucesso")
            return response.json()["access_token"]
        else:
            print(f"❌ Erro no login: {response.status_code}")
            print(response.text)
            return None
    except Exception as e:
        print(f"❌ Erro no login: {e}")
        return None

def create_jornal(token):
    """Cria um jornal de teste"""
    jornal_data = {
        "titulo": "Jornal de Teste",
        "capa": "https://example.com/capa.jpg",
        "arquivopdf": "https://example.com/jornal.pdf"
    }
    
    headers = {"Authorization": f"Bearer {token}"}
    
    try:
        response = requests.post(f"{BASE_URL}/admin/jornais", json=jornal_data, headers=headers)
        if response.status_code == 200:
            print("✅ Jornal criado com sucesso")
            return response.json()
        else:
            print(f"❌ Erro ao criar jornal: {response.status_code}")
            print(response.text)
            return None
    except Exception as e:
        print(f"❌ Erro ao criar jornal: {e}")
        return None

def main():
    """Função principal de teste"""
    print("🧪 Iniciando testes da API Jornal Destaque")
    print("=" * 50)
    
    # Teste 1: Health check
    print("\n1. Testando health check...")
    if not test_health():
        print("❌ API não está funcionando. Verifique se o servidor está rodando.")
        return
    
    # Teste 2: Criar admin
    print("\n2. Criando usuário admin...")
    admin = create_admin()
    if not admin:
        print("❌ Não foi possível criar admin")
        return
    
    # Teste 3: Login
    print("\n3. Fazendo login...")
    token = login_admin()
    if not token:
        print("❌ Não foi possível fazer login")
        return
    
    # Teste 4: Criar jornal
    print("\n4. Criando jornal de teste...")
    jornal = create_jornal(token)
    if not jornal:
        print("❌ Não foi possível criar jornal")
        return
    
    print("\n" + "=" * 50)
    print("🎉 Todos os testes básicos passaram!")
    print("💡 A API está funcionando corretamente")
    print("📚 Acesse http://localhost:8000/docs para ver a documentação completa")

if __name__ == "__main__":
    main()
