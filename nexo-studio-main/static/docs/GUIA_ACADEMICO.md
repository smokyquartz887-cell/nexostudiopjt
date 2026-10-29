# Guia acadêmico completo — Nexo Studio

> **Objetivo didático:** compreender como uma aplicação web full-stack é organizada e como alterar, ajustar, testar e explicar cada parte. Este guia descreve a implementação incluída no projeto e diferencia recursos implementados de melhorias recomendadas.

## 1. Visão geral

O Nexo Studio é um protótipo SaaS educacional para pequenos e médios negócios. Um usuário cria uma conta, configura um negócio, personaliza cores e conteúdo, cadastra páginas, produtos/serviços e movimentações, acompanha indicadores e configura uma base de perguntas e respostas para o chatbot do site público.

### Funcionalidades

| Área | O que faz | Conceitos estudados |
|---|---|---|
| Autenticação | Cadastro, login e logout | Sessão, usuário, autorização |
| Identidade do negócio | Nome, setor, descrição, contatos, cores, logotipo e imagem | ModelForm, upload, validação |
| Páginas e menus | Criação, edição, ordenação e visibilidade | CRUD, relacionamento 1:N |
| Catálogo | Produtos e serviços com preço e estado ativo | Modelos, DecimalField, formulários |
| Movimentações | Leads, vendas, agendamentos, tarefas e status | Datas, filtros e operações |
| Dashboard | Contadores, receita concluída e atividades recentes | Agregações ORM e indicadores |
| Relatórios | Resumos por tipo/status e exportação CSV | Consultas, agrupamento, exportação |
| Biblioteca visual | Quatro sugestões por setor e imagem própria | Dados de referência, upload |
| Chatbot e FAQ | Cadastro manual/importação CSV de Q&A | Base de conhecimento, matching |
| API JSON | Endpoint público para perguntas | HTTP, JSON, integração frontend/backend |
| Camada de segurança | Validação, rate limiting, upload, auditoria e configuração | Defesa em profundidade, testes e OWASP |
| Site público | Renderiza o conteúdo personalizado do negócio | Templates, contexto e CSS dinâmico |

## 2. Preparar no GitHub Codespaces

Abra o repositório no Codespaces e abra um terminal na pasta raiz `nexo-studio`.

```bash
python -m pip install -r requirements.txt
python manage.py makemigrations studio
python manage.py migrate
python manage.py check
python manage.py runserver 0.0.0.0:8000
```

**O que cada comando faz**

- `python -m pip install -r requirements.txt`: instala as bibliotecas declaradas no arquivo de dependências. `-r` significa ler uma lista de requisitos.
- `makemigrations studio`: compara os modelos Python com o histórico de migrações e gera operações de alteração de esquema para o app `studio`.
- `migrate`: aplica as migrações ao SQLite e cria/ajusta tabelas.
- `check`: executa verificações do projeto sem iniciar o servidor.
- `runserver 0.0.0.0:8000`: inicia o servidor de desenvolvimento escutando na porta 8000, que o Codespaces pode encaminhar para o navegador.

Na aba **Ports/Portas**, abra a porta 8000. Para parar o servidor, volte ao terminal e pressione `Ctrl+C`.

> Em desenvolvimento, cada Codespace possui seu próprio banco SQLite e seus próprios arquivos de mídia. Não compartilhe dados pessoais reais em atividades de sala.

## 3. Estrutura de diretórios

```text
nexo-studio/
├── manage.py                 # ponto de entrada dos comandos Django
├── requirements.txt          # dependências Python
├── config/                   # configurações globais e roteamento raiz
├── security/                 # controles de segurança reutilizáveis
│   ├── authorization.py       # autorização por proprietário/negócio
│   ├── validation.py          # validação de JSON e perguntas
│   ├── api_security.py        # rate limiting da API pública
│   ├── uploads.py             # validação de conteúdo de imagens
│   ├── audit.py               # eventos de segurança
│   ├── middleware.py          # cabeçalhos HTTP
│   └── checks.py              # verificações de configuração
├── studio/                   # regras de negócio da aplicação
│   ├── models.py             # estrutura persistida no SQLite
│   ├── forms.py              # formulários e validação
│   ├── views.py              # fluxo HTTP, regras e respostas
│   ├── urls.py               # rotas do app
│   ├── sector_images.py      # sugestões visuais por setor
│   └── migrations/           # histórico de alterações do banco
├── templates/studio/         # HTML renderizado pelo Django
├── static/css/app.css        # estilo da interface
├── static/js/app.js          # interações do painel
├── static/docs/modelo_faq.csv# exemplo de importação de perguntas
├── media/                    # uploads locais (criado em execução)
└── docs/                     # documentação acadêmica e diagramas
```

## 4. Como uma requisição funciona

1. O navegador solicita uma URL.
2. `config/urls.py` encaminha a URL para `studio/urls.py`.
3. A rota seleciona uma função em `studio/views.py`.
4. A view valida o usuário e os dados, consulta ou grava modelos.
5. O Django consulta o SQLite via ORM.
6. A view retorna HTML de um template ou JSON para uma API.
7. O navegador exibe a página ou atualiza o chat.

Veja o diagrama em [`diagramas/fluxo-requisicao.svg`](diagramas/fluxo-requisicao.svg). Para estudar os controles de segurança, consulte [`SEGURANCA.md`](SEGURANCA.md), que contém diagramas embutidos em Markdown, exemplos e exercícios.

## 5. Modelos e banco de dados

| Modelo | Responsabilidade | Relacionamentos |
|---|---|---|
| `User` (Django) | Conta e autenticação | Um usuário pode ser responsável por negócios |
| `Business` | Perfil, setor e identidade visual | Pertence a um `User` |
| `Page` | Página/aba do site | Pertence a um negócio |
| `Offering` | Produto ou serviço | Pertence a um negócio |
| `Activity` | Movimento operacional | Pertence a um negócio |
| `FAQItem` | Pergunta, resposta, palavras-chave e status | Pertence a um negócio |
| `ChatInteraction` | Pergunta recebida, resposta enviada e FAQ correspondente | Pertence a um negócio; FAQ correspondente é opcional |

A chave estrangeira (`ForeignKey`) representa o relacionamento muitos-para-um. Quando um negócio é excluído, seus registros relacionados são excluídos por `on_delete=models.CASCADE`. A FAQ referenciada por uma interação usa `SET_NULL` para preservar o histórico mesmo se a pergunta for removida.

**Exercício:** abra `studio/models.py`, localize `FAQItem` e identifique quais campos são obrigatórios, quais possuem valores padrão e qual restrição impede cadastrar a mesma pergunta duas vezes no mesmo negócio.

## 6. Alterar o projeto com segurança

### Alterar campos do negócio

1. Edite o modelo apropriado em `studio/models.py`.
2. Inclua o campo no `ModelForm` correspondente em `studio/forms.py`.
3. Confira se o template usa o formulário automaticamente ou se precisa exibir o novo campo.
4. Gere e aplique migrações:

```bash
python manage.py makemigrations studio
python manage.py migrate
```

5. Valide com `python manage.py check` e teste no navegador.

### Alterar a aparência

- CSS global: `static/css/app.css`.
- JavaScript geral do painel: `static/js/app.js`.
- Navegação autenticada: `templates/studio/base.html`.
- Página pública personalizada: `templates/studio/public_site.html`.
- Página inicial comercial: `templates/studio/landing.html`.

Para alterar uma cor padrão, localize os valores `primary_color`, `secondary_color` e `accent_color` no modelo `Business` e nos formulários. A página pública injeta as cores salvas pelo proprietário em estilos do site.

### Alterar o menu público

As páginas são registros do modelo `Page`. `menu_label`, `is_visible` e `sort_order` controlam o rótulo, a visibilidade e a ordenação. A view `public_site` consulta apenas páginas visíveis; o template percorre essa lista para renderizar o menu.

### Adicionar uma nova rota

1. Escreva a view em `studio/views.py`.
2. Adicione um `path()` em `studio/urls.py` com nome único.
3. Crie ou ajuste um template em `templates/studio/`.
4. Use `{% url 'nome_da_rota' %}` no HTML em vez de codificar links repetidos.
5. Teste a rota como usuário autenticado e não autenticado, quando aplicável.

## 7. Chatbot e base de perguntas e respostas

O chatbot público utiliza uma API JSON do próprio projeto. O responsável pelo negócio pode cadastrar perguntas manualmente na opção **Chatbot e FAQ** ou importar um CSV. Os dados ficam no SQLite; as perguntas pertencem a um negócio específico.

### Formato CSV

Use UTF-8 e separador ponto e vírgula. Colunas obrigatórias: `pergunta` e `resposta`. Colunas opcionais: `palavras_chave` e `ativa`.

```csv
pergunta;resposta;palavras_chave;ativa
Qual é o horário de atendimento?;Atendemos de segunda a sexta, das 9h às 18h.;horário, funcionamento, abre;sim
Quais formas de pagamento são aceitas?;Aceitamos Pix e cartões.;pagamento, pix, cartão;sim
Como posso entrar em contato?;Envie e-mail para contato@exemplo.com.;contato, telefone, e-mail;sim
```

O arquivo de exemplo está em `static/docs/modelo_faq.csv`.

### Como o matching funciona

1. A API recebe a pergunta do visitante em JSON.
2. O texto é normalizado (minúsculas, sem acentos e sem pontuação).
3. A aplicação compara a pergunta com o texto das FAQs e as palavras-chave ativas.
4. Se encontrar uma correspondência, devolve a resposta cadastrada.
5. Se não encontrar, informa que não há resposta específica e mostra os canais de contato configurados.
6. A pergunta e a resposta são registradas em `ChatInteraction` para análise posterior.

**Limitação intencional para ensino:** esta implementação é um chatbot baseado em regras e correspondência textual. Ela não utiliza IA generativa, não consulta a internet e não inventa respostas. A estrutura pode ser expandida futuramente para um provedor de IA, mantendo a FAQ como fonte de referência e adicionando controles de segurança.

### Endpoint da API

`POST /api/chat/<slug-do-negocio>/`

Cabeçalho: `Content-Type: application/json`

Corpo de exemplo:

```json
{"pergunta": "Qual o horário de atendimento?"}
```

Resposta de exemplo:

```json
{
  "resposta": "Atendemos de segunda a sexta, das 9h às 18h.",
  "encontrada": true,
  "negocio": "Meu negócio"
}
```

A documentação resumida também está disponível em `/api/documentacao/`. A API pública é vinculada ao slug de um negócio publicado, para que não consulte FAQs de outro negócio.

## 8. Uploads e arquivos

O upload do logotipo e da imagem de destaque é tratado por `BusinessForm`, que valida tipo MIME e tamanho declarado. O Django grava os arquivos sob `MEDIA_ROOT` e persiste no banco o caminho relativo.

Em um ambiente real, não confie apenas no `content_type` enviado pelo navegador: valide o conteúdo do arquivo, limite dimensões, renomeie arquivos, considere antivírus e armazene mídias em serviço de objetos. Em produção, configure `DEBUG=False`, `SECRET_KEY` via variável de ambiente, hosts confiáveis, HTTPS e política de backup.

## 9. Dashboard e relatórios

O dashboard usa consultas do ORM (`count()`, `filter()` e `aggregate(Sum(...))`) para calcular quantidade de atividades, itens em aberto e receita de vendas concluídas. O relatório agrupa registros por tipo e status e o endpoint de exportação produz CSV.

**Exercício:** inclua no dashboard um indicador de perguntas recebidas pelo chatbot nos últimos sete dias, consultando `ChatInteraction` com filtro por data.

## 10. Segurança, privacidade e limites do protótipo

- A autenticação e as sessões são fornecidas pelo Django.
- As telas de gestão usam `login_required`; as consultas devem sempre limitar registros ao negócio do usuário.
- O endpoint de chat é público por natureza; para produção, implemente limitação de requisições, proteção contra abuso, monitoramento e política de retenção.
- Não solicite nem armazene senhas, dados financeiros sensíveis, documentos pessoais ou informações médicas em perguntas do chatbot.
- O projeto é acadêmico e usa SQLite. Para SaaS comercial com muitos clientes, avalie PostgreSQL, armazenamento de objetos, backups, observabilidade e controles de isolamento mais rigorosos.
- Não há cobrança, gestão de planos ou provisionamento de domínio real nesta versão.

## 11. Roteiro de avaliação sugerido

1. Criar usuário e negócio.
2. Alterar paleta, setor e imagem.
3. Criar uma página e definir sua ordem no menu.
4. Cadastrar um produto ou serviço.
5. Registrar uma movimentação e verificar dashboard/relatório.
6. Cadastrar três perguntas e respostas.
7. Importar perguntas por CSV.
8. Publicar o site, abrir o chatbot e testar pergunta conhecida e desconhecida.
9. Conferir que a interação foi salva no banco.
10. Apresentar um diagrama e explicar o fluxo completo de uma requisição.

## 12. Próximas evoluções possíveis

- Testes automatizados para views, permissões e API.
- Seleção explícita de negócio ativo quando um usuário gerenciar vários negócios.
- Paginação e busca nos cadastros.
- API autenticada para integração administrativa.
- Rate limiting, logs estruturados e alertas.
- Integração opcional com provedor de IA, com chave no ambiente, consentimento e fallback para FAQ.
- Multiusuário por empresa, papéis/permissões, planos e cobrança.
- Migração para PostgreSQL e implantação com HTTPS.


## Testes de segurança multi-tenant

Consulte [TESTES_E_ISOLAMENTO.md](TESTES_E_ISOLAMENTO.md). Os testes verificam acessos cruzados entre dois proprietários. Execute `python manage.py test studio` antes de publicar mudanças.


## Camada de segurança — roteiro didático

Leia [`SEGURANCA.md`](SEGURANCA.md) em conjunto com `security/`. O guia explica cada módulo, os limites da API do chatbot, validação de upload, variáveis de ambiente e testes. Ao alterar uma regra, escreva um teste para o comportamento esperado e outro para o caso de rejeição.
