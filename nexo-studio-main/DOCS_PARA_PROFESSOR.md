# Guia do professor — Nexo Studio

## Objetivos didáticos
- Entender o padrão MTV do Django (models, templates, views).
- Relacionar tabelas usando ForeignKey e compreender o isolamento por proprietário.
- Implementar autenticação, formulários, validação, upload e CRUD.
- Construir interface responsiva com HTML/CSS/JS.
- Calcular indicadores e exportar relatórios CSV.

## Sequência sugerida (6 encontros)
1. Ambiente, rotas, templates e autenticação.
2. Modelos, migrations e CRUD de páginas.
3. Identidade visual, upload e biblioteca de imagens.
4. Catálogo e movimentações.
5. Dashboard, relatórios e CSV.
6. Publicação do site, testes, revisão de segurança e apresentação.

## Atividade de extensão
Cada grupo escolhe um setor e melhora a experiência correspondente: novos campos, páginas, paletas, validações, filtros ou indicadores. Peça aos alunos para explicar cada migration, view, model e template implementado.

## Escopo atual
O projeto é um MVP educacional. Não possui cobrança, planos SaaS, múltiplos membros por empresa, API pública, automação de publicação externa nem proteção de produção completa. A página pública é servida pelo próprio Django.


## Recursos acadêmicos ampliados

A versão atual inclui documentação navegável na barra lateral: **Como alterar e compreender** e **Arquitetura e componentes**. Os documentos-fonte estão em `docs/` e as cópias acessíveis pela interface em `static/docs/`. Os diagramas SVG estão em `docs/diagramas/` e `static/docs/diagramas/`; o Markdown também contém Mermaid para reedição.

### Chatbot e API

- Menu **Chatbot e FAQ**: cadastro, edição, exclusão e importação CSV de perguntas e respostas.
- `POST /api/chat/<slug-do-negocio>/`: recebe JSON com `pergunta`, procura uma resposta entre as FAQs ativas daquele negócio e salva a interação em `ChatInteraction`.
- `/api/documentacao/`: retorna a especificação básica do endpoint em JSON.
- O chatbot é baseado em regras e correspondência textual; não depende de API comercial externa nem de chave secreta. Isso o torna reproduzível em aula. Uma futura integração com LLM deverá ser opcional, configurada por variável de ambiente e com controles de privacidade.

### Preparação

Execute `python manage.py makemigrations studio` e `python manage.py migrate` após baixar o ZIP. O SQLite de cada Codespace é local ao ambiente.
