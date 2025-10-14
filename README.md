# Jornal Destaque - Backend API

API backend para o aplicativo de vendas de jornais desenvolvido com FastAPI, SQLAlchemy e SQLite.

## Funcionalidades

### Upload de Arquivos
- **Capas**: Suporte a JPEG, PNG, GIF, WebP (opcional)
- **PDFs**: Suporte a PDF (obrigatório)
- **Tamanho máximo**: 10MB por arquivo
- **Validação**: Tipos de arquivo e tamanho validados automaticamente
- **Armazenamento**: Arquivos salvos com nomes únicos em diretórios organizados
- **Acesso**: URLs diretas para download dos arquivos

### Para Administradores
- Criação automática de conta admin
- Gerenciamento de jornais (CRUD) com upload de arquivos
- Upload de capas (imagens) e PDFs dos jornais
- Gerenciamento de usuários (listar, editar, excluir)
- Criação de assinaturas para pagamentos físicos
- Listagem de todas as assinaturas

### Para Usuários
- Registro e login
- Visualização de jornais disponíveis
- Filtro de jornais por data
- Criação de assinaturas digitais
- Controle de acesso baseado em assinatura
- Limite de 2 dispositivos por usuário
- Tokens com validade de 24 horas
- Acesso aos arquivos via URLs diretas

### Tipos de Assinatura
- Diária
- Semanal
- Mensal
- Anual

## Instalação

1. Clone o repositório
2. Instale as dependências:
```bash
pip install -r requirements.txt
```

3. Configure as variáveis de ambiente (opcional):
```bash
cp .env.example .env
```

4. Execute o servidor:
```bash
python main.py
```

## Estrutura do Projeto

```
JDBack/
├── main.py              # Arquivo principal da aplicação
├── database.py          # Configuração do banco de dados
├── models.py            # Modelos SQLAlchemy
├── schemas.py           # Schemas Pydantic
├── auth.py              # Sistema de autenticação
├── file_handler.py      # Manipulação de arquivos e upload
├── config.py            # Configurações centralizadas
├── admin_routes.py      # Rotas para administradores
├── user_routes.py       # Rotas para usuários
├── run.py               # Script de execução
├── test_api.py          # Testes básicos da API
├── exemplo_upload.py    # Exemplo de uso com upload
├── requirements.txt     # Dependências do projeto
├── INSTALACAO.md        # Guia de instalação
├── exemplos_uso.md      # Exemplos de uso da API
└── README.md           # Este arquivo
```

## Endpoints

### Autenticação
- `POST /user/register` - Registro de usuário
- `POST /user/login` - Login
- `POST /user/logout` - Logout

### Usuários
- `GET /user/me` - Informações do usuário atual
- `GET /user/jornais` - Lista jornais disponíveis
- `GET /user/jornais/{id}` - Obtém jornal específico
- `POST /user/subscriptions` - Cria assinatura digital
- `GET /user/my-subscriptions` - Lista assinaturas do usuário

### Administradores
- `POST /admin/create-admin` - Cria conta admin
- `POST /admin/jornais` - Cria jornal (multipart/form-data)
- `GET /admin/jornais` - Lista todos os jornais
- `GET /admin/jornais/{id}` - Obtém jornal específico
- `PUT /admin/jornais/{id}` - Atualiza jornal (multipart/form-data)
- `DELETE /admin/jornais/{id}` - Remove jornal
- `GET /admin/users` - Lista usuários
- `GET /admin/users/{id}` - Obtém usuário específico
- `PUT /admin/users/{id}` - Atualiza usuário
- `DELETE /admin/users/{id}` - Remove usuário
- `POST /admin/subscriptions` - Cria assinatura (pagamento físico)
- `GET /admin/subscriptions` - Lista todas as assinaturas

## Segurança

- Autenticação JWT com python-jose
- Senhas criptografadas com bcrypt
- Controle de sessões por dispositivo (máximo 2)
- Tokens com expiração de 24 horas
- Middleware CORS configurado

## Banco de Dados

O projeto utiliza SQLite com as seguintes tabelas:
- `users` - Usuários do sistema
- `jornais` - Jornais disponíveis
- `subscriptions` - Assinaturas dos usuários
- `token_sessions` - Controle de sessões ativas

## Primeiros Passos

1. Execute o servidor
2. Crie a conta admin: `POST /admin/create-admin`
3. Faça login como admin para gerenciar o sistema
4. Crie jornais com upload de arquivos e gerencie usuários

## Upload de Arquivos

### Criar Jornal com Upload
```bash
curl -X POST "http://localhost:8000/admin/jornais" \
     -H "Authorization: Bearer SEU_TOKEN" \
     -F "titulo=Meu Jornal" \
     -F "arquivopdf=@jornal.pdf" \
     -F "capa=@capa.jpg"
```

### Atualizar Jornal
```bash
curl -X PUT "http://localhost:8000/admin/jornais/1" \
     -H "Authorization: Bearer SEU_TOKEN" \
     -F "titulo=Novo Título" \
     -F "capa=@nova_capa.jpg"
```
