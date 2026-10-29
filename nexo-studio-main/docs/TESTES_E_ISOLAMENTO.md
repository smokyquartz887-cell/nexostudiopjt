# Testes de isolamento entre clientes

## Objetivo
Demonstrar que cada usuário só administra os negócios que possui e que o chatbot público responde usando a FAQ do slug solicitado.

## Executar

```bash
python manage.py test studio
```

## Cenários cobertos

| Teste | Comportamento esperado |
|---|---|
| Painel sem autenticação | Redirecionamento para login |
| Cliente A abre página do cliente B | HTTP 404 |
| Cliente A tenta excluir FAQ do cliente B | HTTP 404; registro permanece |
| Chatbot público do negócio A | Usa apenas FAQ vinculada ao negócio A |
| Cliente A seleciona negócio do cliente B | HTTP 404 |
| Pergunta igual em dois negócios | Permitida, pois unicidade é por negócio |

## Limites
Estes testes são uma base de regressão, não substituem revisão de segurança. Acrescente testes para todos os modelos, exports, upload, sessão, administração e endpoints antes de produção.
