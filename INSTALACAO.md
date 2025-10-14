# Instalação e Configuração - Jornal Destaque API

## Pré-requisitos

- Python 3.8 ou superior
- pip (gerenciador de pacotes Python)

## Instalação

### 1. Clone ou baixe o projeto
```bash
cd JDBack
```

### 2. Instale as dependências
```bash
pip install -r requirements.txt
```

### 3. Configure as variáveis de ambiente (opcional)
```bash
# Copie o arquivo de exemplo
cp .env.example .env

# Edite o arquivo .env com suas configurações
```

### 4. Execute o servidor

#### Opção 1: Usando o script de execução
```bash
python run.py
```

#### Opção 2: Execução direta
```bash
python main.py
```

#### Opção 3: Usando uvicorn diretamente
```bash
uvicorn main:app --host 0.0.0.0 --port 8000 --reload
```

## Primeiros Passos

### 1. Verificar se a API está funcionando
Acesse: http://localhost:8000/health

### 2. Criar o usuário administrador
```bash
curl -X POST "http://localhost:8000/admin/create-admin" \
     -H "Content-Type: application/json" \
     -d '{
       "nome": "Administrador",
       "telefone": "11999999999",
       "email": "admin@jornaldestaque.com",
       "senha": "admin123"
     }'
```

### 3. Fazer login como admin
```bash
curl -X POST "http://localhost:8000/user/login" \
     -H "Content-Type: application/json" \
     -d '{
       "email": "admin@jornaldestaque.com",
       "senha": "admin123"
     }'
```

### 4. Usar o token retornado para acessar rotas protegidas
```bash
curl -X GET "http://localhost:8000/admin/jornais" \
     -H "Authorization: Bearer SEU_TOKEN_AQUI"
```

## Documentação da API

Após iniciar o servidor, acesse:
- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

## Testes

Execute o script de teste básico:
```bash
python test_api.py
```

## Estrutura do Banco de Dados

O banco SQLite será criado automaticamente na primeira execução com as seguintes tabelas:
- `users` - Usuários do sistema
- `jornais` - Jornais disponíveis
- `subscriptions` - Assinaturas dos usuários
- `token_sessions` - Controle de sessões ativas

## Configurações Importantes

### Segurança
- **SECRET_KEY**: Altere para uma chave segura em produção
- **ACCESS_TOKEN_EXPIRE_MINUTES**: Tempo de validade do token (padrão: 1440 minutos = 24 horas)
- **MAX_DEVICES_PER_USER**: Máximo de dispositivos por usuário (padrão: 2)

### Banco de Dados
- **DATABASE_URL**: URL de conexão com o banco (padrão: SQLite local)

## Problemas Comuns

### Erro de importação
```bash
# Se houver erro de importação, verifique se instalou todas as dependências
pip install -r requirements.txt
```

### Porta já em uso
```bash
# Se a porta 8000 estiver em uso, use outra porta
uvicorn main:app --port 8001
```

### Problemas de permissão
```bash
# No Windows, execute como administrador se necessário
# No Linux/Mac, use sudo se necessário
```

## Produção

Para usar em produção:
1. Configure uma SECRET_KEY segura
2. Use um banco de dados mais robusto (PostgreSQL, MySQL)
3. Configure HTTPS
4. Use um servidor WSGI como Gunicorn
5. Configure proxy reverso (Nginx)
