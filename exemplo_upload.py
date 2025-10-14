#!/usr/bin/env python3
"""
Exemplo de como usar a API com upload de arquivos
"""
import requests
import json

# Configurações
BASE_URL = "http://localhost:8000"

def login_admin():
    """Faz login como admin"""
    login_data = {
        "email": "admin@jornaldestaque.com",
        "senha": "admin123"
    }
    
    response = requests.post(f"{BASE_URL}/user/login", json=login_data)
    if response.status_code == 200:
        return response.json()["access_token"]
    else:
        print(f"Erro no login: {response.status_code}")
        print(response.text)
        return None

def create_jornal_with_files(token):
    """Cria um jornal com upload de arquivos"""
    
    # Dados do formulário
    data = {
        "titulo": "Jornal de Exemplo com Upload"
    }
    
    # Arquivos para upload
    files = {
        "arquivopdf": ("jornal.pdf", open("exemplo.pdf", "rb"), "application/pdf"),
        "capa": ("capa.jpg", open("exemplo_capa.jpg", "rb"), "image/jpeg")
    }
    
    headers = {
        "Authorization": f"Bearer {token}"
    }
    
    try:
        response = requests.post(
            f"{BASE_URL}/admin/jornais",
            data=data,
            files=files,
            headers=headers
        )
        
        if response.status_code == 200:
            print("✅ Jornal criado com sucesso!")
            print(json.dumps(response.json(), indent=2, ensure_ascii=False))
        else:
            print(f"❌ Erro ao criar jornal: {response.status_code}")
            print(response.text)
    
    except FileNotFoundError as e:
        print(f"❌ Arquivo não encontrado: {e}")
        print("💡 Certifique-se de ter os arquivos 'exemplo.pdf' e 'exemplo_capa.jpg' na pasta")
    
    finally:
        # Fecha os arquivos
        for file_tuple in files.values():
            if hasattr(file_tuple[1], 'close'):
                file_tuple[1].close()

def update_jornal_with_files(token, jornal_id):
    """Atualiza um jornal com novos arquivos"""
    
    # Dados do formulário
    data = {
        "titulo": "Jornal Atualizado com Upload"
    }
    
    # Apenas a capa (PDF não será atualizado)
    files = {
        "capa": ("nova_capa.jpg", open("exemplo_capa.jpg", "rb"), "image/jpeg")
    }
    
    headers = {
        "Authorization": f"Bearer {token}"
    }
    
    try:
        response = requests.put(
            f"{BASE_URL}/admin/jornais/{jornal_id}",
            data=data,
            files=files,
            headers=headers
        )
        
        if response.status_code == 200:
            print("✅ Jornal atualizado com sucesso!")
            print(json.dumps(response.json(), indent=2, ensure_ascii=False))
        else:
            print(f"❌ Erro ao atualizar jornal: {response.status_code}")
            print(response.text)
    
    except FileNotFoundError as e:
        print(f"❌ Arquivo não encontrado: {e}")
    
    finally:
        # Fecha os arquivos
        for file_tuple in files.values():
            if hasattr(file_tuple[1], 'close'):
                file_tuple[1].close()

def main():
    """Função principal"""
    print("📁 Exemplo de Upload de Arquivos - Jornal Destaque")
    print("=" * 60)
    
    # Login
    print("\n1. Fazendo login...")
    token = login_admin()
    if not token:
        return
    
    print("✅ Login realizado com sucesso!")
    
    # Criar jornal com upload
    print("\n2. Criando jornal com upload de arquivos...")
    create_jornal_with_files(token)
    
    # Atualizar jornal
    print("\n3. Atualizando jornal (apenas capa)...")
    update_jornal_with_files(token, 1)  # Assumindo que o jornal tem ID 1
    
    print("\n" + "=" * 60)
    print("🎉 Exemplo concluído!")
    print("💡 Verifique a documentação em http://localhost:8000/docs")

if __name__ == "__main__":
    main()
