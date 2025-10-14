# Exemplos de Uso da API - Jornal Destaque

## 1. Fluxo Completo de Administrador

### Criar Admin
```bash
curl -X POST "http://localhost:8000/admin/create-admin" \
     -H "Content-Type: application/json" \
     -d '{
       "nome": "João Silva",
       "telefone": "11999999999",
       "email": "joao@jornaldestaque.com",
       "senha": "admin123"
     }'
```

### Login do Admin
```bash
curl -X POST "http://localhost:8000/user/login" \
     -H "Content-Type: application/json" \
     -d '{
       "email": "joao@jornaldestaque.com",
       "senha": "admin123"
     }'
```

### Criar Jornal com Upload de Arquivos (com token)
```bash
curl -X POST "http://localhost:8000/admin/jornais" \
     -H "Authorization: Bearer SEU_TOKEN_AQUI" \
     -F "titulo=Notícias do Dia" \
     -F "capa=@/caminho/para/capa.jpg" \
     -F "arquivopdf=@/caminho/para/jornal.pdf"
```

**Nota:** O campo `arquivopdf` é obrigatório, `capa` é opcional.

### Listar Jornais
```bash
curl -X GET "http://localhost:8000/admin/jornais" \
     -H "Authorization: Bearer SEU_TOKEN_AQUI"
```

### Listar Usuários
```bash
curl -X GET "http://localhost:8000/admin/users" \
     -H "Authorization: Bearer SEU_TOKEN_AQUI"
```

## 2. Fluxo Completo de Usuário

### Registrar Usuário
```bash
curl -X POST "http://localhost:8000/user/register" \
     -H "Content-Type: application/json" \
     -d '{
       "nome": "Maria Santos",
       "telefone": "11888888888",
       "email": "maria@email.com",
       "senha": "senha123",
       "tipo_subscricao": "mensal"
     }'
```

### Login do Usuário
```bash
curl -X POST "http://localhost:8000/user/login" \
     -H "Content-Type: application/json" \
     -d '{
       "email": "maria@email.com",
       "senha": "senha123"
     }'
```

### Ver Jornais Disponíveis
```bash
curl -X GET "http://localhost:8000/user/jornais" \
     -H "Authorization: Bearer SEU_TOKEN_AQUI"
```

### Filtrar Jornais por Data
```bash
curl -X GET "http://localhost:8000/user/jornais?data_inicio=2024-01-01&data_fim=2024-01-31" \
     -H "Authorization: Bearer SEU_TOKEN_AQUI"
```

### Criar Assinatura Digital
```bash
curl -X POST "http://localhost:8000/user/subscriptions" \
     -H "Content-Type: application/json" \
     -H "Authorization: Bearer SEU_TOKEN_AQUI" \
     -d '{
       "subscription_type": "mensal",
       "user_id": 1
     }'
```

### Ver Minhas Assinaturas
```bash
curl -X GET "http://localhost:8000/user/my-subscriptions" \
     -H "Authorization: Bearer SEU_TOKEN_AQUI"
```

## 3. Funcionalidades de Admin

### Dar Acesso Físico a Usuário
```bash
curl -X POST "http://localhost:8000/admin/subscriptions" \
     -H "Content-Type: application/json" \
     -H "Authorization: Bearer SEU_TOKEN_AQUI" \
     -d '{
       "user_id": 2,
       "subscription_type": "anual",
       "payment_method": "fisico"
     }'
```

### Editar Usuário
```bash
curl -X PUT "http://localhost:8000/admin/users/2" \
     -H "Content-Type: application/json" \
     -H "Authorization: Bearer SEU_TOKEN_AQUI" \
     -d '{
       "nome": "Maria Santos Atualizada",
       "tipo_subscricao": "anual"
     }'
```

### Editar Jornal com Upload de Arquivos
```bash
curl -X PUT "http://localhost:8000/admin/jornais/1" \
     -H "Authorization: Bearer SEU_TOKEN_AQUI" \
     -F "titulo=Notícias Atualizadas" \
     -F "capa=@/caminho/para/nova-capa.jpg"
```

**Nota:** Todos os campos são opcionais no update. Apenas os arquivos fornecidos serão atualizados.

### Desativar Usuário
```bash
curl -X DELETE "http://localhost:8000/admin/users/2" \
     -H "Authorization: Bearer SEU_TOKEN_AQUI"
```

### Desativar Jornal
```bash
curl -X DELETE "http://localhost:8000/admin/jornais/1" \
     -H "Authorization: Bearer SEU_TOKEN_AQUI"
```

## 4. Tipos de Assinatura Disponíveis

- `"diario"` - Acesso por 1 dia
- `"semanal"` - Acesso por 1 semana
- `"mensal"` - Acesso por 30 dias
- `"anual"` - Acesso por 365 dias

## 5. Respostas de Exemplo

### Login Bem-sucedido
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer",
  "expires_in": 86400
}
```

### Jornal Criado
```json
{
  "id": 1,
  "titulo": "Notícias do Dia",
  "capa": "https://exemplo.com/capa.jpg",
  "arquivopdf": "https://exemplo.com/jornal.pdf",
  "data_publicacao": "2024-01-15T10:30:00",
  "is_active": true,
  "created_at": "2024-01-15T10:30:00",
  "updated_at": null
}
```

### Usuário Registrado
```json
{
  "id": 1,
  "nome": "Maria Santos",
  "telefone": "11888888888",
  "email": "maria@email.com",
  "tipo_subscricao": "mensal",
  "tipo_usuario": "user",
  "is_active": true,
  "created_at": "2024-01-15T10:30:00",
  "updated_at": null
}
```

## 6. Códigos de Status HTTP

- `200` - Sucesso
- `201` - Criado com sucesso
- `400` - Dados inválidos
- `401` - Não autorizado
- `403` - Acesso negado
- `404` - Recurso não encontrado
- `422` - Erro de validação

## 7. Upload de Arquivos

### Tipos de Arquivo Suportados

**Para Capas:**
- JPEG (.jpg, .jpeg)
- PNG (.png)
- GIF (.gif)
- WebP (.webp)

**Para PDFs:**
- PDF (.pdf)

### Tamanho Máximo
- Tamanho máximo por arquivo: 10MB

### Estrutura de Diretórios
```
uploads/
├── covers/     # Capas dos jornais
└── pdfs/       # Arquivos PDF dos jornais
```

### Exemplo com Python (requests)
```python
import requests

# Dados do formulário
data = {
    "titulo": "Meu Jornal"
}

# Arquivos para upload
files = {
    "arquivopdf": ("jornal.pdf", open("jornal.pdf", "rb"), "application/pdf"),
    "capa": ("capa.jpg", open("capa.jpg", "rb"), "image/jpeg")  # Opcional
}

headers = {
    "Authorization": "Bearer SEU_TOKEN_AQUI"
}

response = requests.post(
    "http://localhost:8000/admin/jornais",
    data=data,
    files=files,
    headers=headers
)
```

### URLs de Acesso aos Arquivos
Após o upload, os arquivos ficam disponíveis em:
- `http://localhost:8000/files/covers/nome_do_arquivo.jpg`
- `http://localhost:8000/files/pdfs/nome_do_arquivo.pdf`

## 8. Observações Importantes

1. **Tokens**: Todos os tokens expiram em 24 horas
2. **Dispositivos**: Máximo de 2 dispositivos por usuário
3. **Acesso**: Usuários só podem acessar jornais do dia atual sem assinatura
4. **Assinaturas**: Podem ser criadas digitalmente ou fisicamente (apenas admin)
5. **Admin**: Apenas um admin pode existir no sistema
6. **Upload**: Arquivos são salvos com nomes únicos para evitar conflitos
7. **Limpeza**: Arquivos antigos são removidos automaticamente ao deletar/atualizar jornais
