# API RESTful Completa com JWT

Uma API desenvolvida com FastAPI que oferece autenticação JWT, operações CRUD e integração com Stripe para pagamentos.

## Recursos
- Autenticação JWT segura.
- CRUD completo para gerenciamento de recursos.
- Integração com Stripe para processamento de pagamentos.

## Como Configurar
1. Clone o repositório:  
   git clone <url-do-repositorio>
2. Instale as dependências:  
   pip install -r requirements.txt
3. Configure as variáveis de ambiente (arquivo .env):  
   - SECRET_KEY
   - STRIPE_API_KEY
4. Execute o servidor:  
   uvicorn main:app --reload

## Endpoints Principais
- POST /token - Gerar JWT.
- GET /items - Listar itens.
- POST /payments/stripe - Processar pagamentos via Stripe.
