# Nexo Studio — versão 3

## Alterações

- Seleção do negócio ativo por sessão, com validação de que o negócio pertence ao usuário autenticado.
- Seletor de negócio no menu lateral para usuários que administram mais de um negócio.
- Remoção de links duplicados de FAQ/API no menu lateral.
- Testes automatizados de regressão para autenticação, acesso cruzado a páginas e FAQs, seleção de negócio e isolamento das respostas do chatbot.
- Guia de execução dos testes e explicação dos limites de segurança.

## Testes incluídos

`studio/tests.py` usa o `TestCase` do Django e pode ser executado com `python manage.py test studio`.

## Validação realizada nesta geração

- Compilação sintática dos arquivos Python com `python -m compileall`.
- O ambiente de geração não tinha Django instalado; portanto, a suíte de testes Django não foi executada aqui. Execute-a no Codespaces depois de instalar `requirements.txt`.

## Limites conhecidos antes de produção

- O projeto é educacional e não deve ser exposto como SaaS comercial sem revisão de segurança.
- Configurar segredo por variável de ambiente, `DEBUG=False`, hosts permitidos, HTTPS, política de privacidade e controles de abuso/rate limit na API pública.
- A validação de upload deve ser reforçada por inspeção real do conteúdo, além de extensão/MIME e limite de tamanho.
- Avaliar permissões do Django Admin, backups e retenção de conversas do chatbot.
