#!/usr/bin/env python3
"""
Script de inicialização do Jornal Destaque API
"""
import uvicorn
import os
import sys

def main():
    """Função principal para executar o servidor"""
    
    # Verifica se o arquivo .env existe
    if not os.path.exists('.env'):
        print("⚠️  Arquivo .env não encontrado. Usando configurações padrão.")
        print("💡 Para configurar variáveis de ambiente, copie .env.example para .env")
    
    # Configurações do servidor
    host = os.getenv("HOST", "0.0.0.0")
    port = int(os.getenv("PORT", "8000"))
    reload = os.getenv("RELOAD", "true").lower() == "true"
    
    print(f"🚀 Iniciando Jornal Destaque API...")
    print(f"📍 Servidor rodando em: http://{host}:{port}")
    print(f"📚 Documentação da API: http://{host}:{port}/docs")
    print(f"🔄 Auto-reload: {'Ativado' if reload else 'Desativado'}")
    print("-" * 50)
    
    try:
        uvicorn.run(
            "main:app",
            host=host,
            port=port,
            reload=reload,
            log_level="info"
        )
    except KeyboardInterrupt:
        print("\n👋 Servidor interrompido pelo usuário")
    except Exception as e:
        print(f"❌ Erro ao iniciar servidor: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
