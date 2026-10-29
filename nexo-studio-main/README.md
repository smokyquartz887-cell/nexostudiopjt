# Nexo Studio — Construtor de Sites para Pequenos Negócios

Projeto didático em Python, Django, SQLite, HTML, CSS e JavaScript. A aplicação permite criar uma conta, configurar um negócio, personalizar identidade visual, selecionar imagens sugeridas por setor, administrar páginas, cadastrar produtos/serviços, registrar movimentações, consultar relatórios e publicar uma página de apresentação.

## Requisitos
- Python 3.10+ (recomendado Python 3.12)
- Internet para carregar fontes e imagens demonstrativas externas

## Executar no GitHub Codespaces
No terminal, a partir da pasta raiz do projeto:

```bash
python -m pip install -r requirements.txt
python manage.py makemigrations studio
python manage.py migrate
python manage.py createsuperuser  # opcional, para o /admin/
python manage.py runserver 0.0.0.0:8000
```

Abra a aba **Ports**, localize a porta `8000` e abra o navegador. Para começar, clique em **Começar grátis**, crie uma conta e configure o negócio.

## Funcionalidades
- Cadastro e autenticação de usuário
- Isolamento das consultas pelo usuário autenticado (cada usuário acessa seu próprio negócio)
- Cadastro e edição do negócio, cores, setor, estilo, logotipo e upload de imagem de destaque
- Quatro sugestões de imagem por setor (referências externas demonstrativas)
- CRUD de páginas do site e itens de catálogo
- CRUD de movimentações: contatos, vendas, agendamentos, tarefas e outros
- Dashboard com KPIs, atividades recentes e gráfico semanal
- Relatório por tipo/status e exportação CSV
- Publicação do site em `/s/<slug>/` quando a opção Publicado estiver habilitada
- Interface responsiva com navegação móvel

## Roteiro para alunos
1. Criar uma conta.
2. Configurar o negócio e selecionar setor e cores.
3. Abrir Biblioteca de imagens e escolher uma sugestão; ou enviar uma imagem própria em Identidade visual.
4. Cadastrar produtos/serviços e páginas.
5. Registrar movimentações e observar o dashboard.
6. Abrir Relatórios e exportar CSV.
7. Habilitar **Publicado** em Identidade visual e abrir o site pelo botão **Ver site**.

## Observações de segurança e escopo
Este é um MVP educacional para execução local/Codespaces, não um SaaS pronto para produção. Antes de publicar na internet, configure `SECRET_KEY` via variável de ambiente, `DEBUG=False`, `ALLOWED_HOSTS`, HTTPS, backups, política de retenção, proteção de upload, limites de armazenamento, testes, monitoramento e banco adequado. O exemplo de tenancy é por proprietário e suporta um negócio principal por conta na interface atual. Não inclui cobrança/assinaturas, e-mail transacional, CDN nem pipeline de deploy.

As sugestões de imagens usam URLs externas demonstrativas; confirme licenças e direitos de uso antes de uso comercial. Uploads têm validação de tipo e tamanho no formulário, mas uma implantação pública exige validação adicional e armazenamento seguro.


## Recursos acadêmicos adicionados
- Chatbot público com API JSON em `/api/chat/<slug>/`.
- Cadastro manual de perguntas e respostas no menu **Chatbot e FAQ**.
- Importação de perguntas por CSV (modelo em `static/docs/modelo_faq.csv`).
- Registro das interações no SQLite.
- Documentação completa: `docs/GUIA_ACADEMICO.md` e `docs/ARQUITETURA.md`. Também há links na barra lateral após entrar no painel, incluindo **Camada de segurança** com diagramas embutidos em Markdown.
- Diagramas Mermaid e SVGs em `docs/diagramas/`.

**Nota técnica:** o chatbot é baseado em correspondência de perguntas/palavras-chave armazenadas no banco; não é um modelo generativo e não exige chave de API externa. A API JSON é interna ao projeto.


## Versão 3 — segurança e validação

Esta versão adiciona seleção de negócio ativo por sessão, bloqueada ao proprietário autenticado, remove itens duplicados do menu e inclui testes automatizados de isolamento em `studio/tests.py`.

### Inicialização no Codespaces

```bash
python -m pip install -r requirements.txt
python manage.py migrate
python manage.py check
python manage.py test studio
python manage.py runserver 0.0.0.0:8000
```

O Django sincroniza o app ainda sem migrações versionadas durante `migrate`, mas para o fluxo acadêmico recomenda-se gerar e versionar migrações ao alterar modelos (`python manage.py makemigrations studio`).

**Limite importante:** esta é uma versão didática para ambiente de desenvolvimento. Antes de produção, configure `SECRET_KEY`, `DEBUG=False`, `ALLOWED_HOSTS`, HTTPS, armazenamento de mídia, política de privacidade, proteção contra abuso da API pública e revisão de segurança. Os testes automatizados ajudam, mas não constituem auditoria de segurança completa.


## Camada de segurança (versão 4)

O pacote `security/` centraliza validação de entradas, rate limiting simples para o chatbot, validação de conteúdo de imagens, auditoria, cabeçalhos HTTP e checks de configuração. Leia [`docs/SEGURANCA.md`](docs/SEGURANCA.md) para conhecer os controles, os diagramas e as limitações.

Depois de instalar as dependências, execute `python manage.py makemigrations studio`, `python manage.py migrate`, `python manage.py check` e `python manage.py test studio`. O protótipo não está pronto para produção sem configurar segredos, HTTPS, hosts, cache compartilhado, política de privacidade e revisão independente.

Arquivo `.env.example` lista as variáveis esperadas, mas o projeto não carrega `.env` automaticamente. Defina as variáveis no terminal, no Codespaces ou no mecanismo de secrets da plataforma. Não adicione o segredo real ao Git.


## Instalação local no Windows (VS Code)

1. Instale Python 3.12 e o VS Code.
2. Extraia o ZIP e abra no VS Code a pasta `nexo-studio-main`, onde está o `manage.py`.
3. No terminal do VS Code, crie e ative o ambiente virtual:

   ```powershell
   py -m venv .venv
   .\.venv\Scripts\Activate.ps1
   ```

   Se o Windows não reconhecer `py`, tente `python` no lugar de `py`. Se o PowerShell bloquear a ativação, feche e abra um terminal novo ou use o terminal Command Prompt e execute `.venv\Scripts\activate.bat`.

4. Instale as dependências:

   ```powershell
   python -m pip install --upgrade pip
   python -m pip install -r requirements.txt
   ```

5. Copie `.env.example` para `.env`:

   ```powershell
   Copy-Item .env.example .env
   ```

6. Abra `.env` e confira `NEXO_DEBUG=1` e `NEXO_ALLOWED_HOSTS=localhost,127.0.0.1`. O projeto carrega esse arquivo automaticamente. Não compartilhe nem publique o `.env`.
7. Prepare o banco e inicie o servidor:

   ```powershell
   python manage.py migrate
   python manage.py check
   python manage.py runserver
   ```

8. Acesse `http://127.0.0.1:8000/` no navegador. Para interromper o servidor, volte ao terminal e pressione `Ctrl+C`.

**Observação:** o arquivo `.env.example` contém valores de exemplo. Para uso local, mantenha a configuração de desenvolvimento; não use `DEBUG=True` nem uma chave de desenvolvimento em um ambiente publicado na internet.
