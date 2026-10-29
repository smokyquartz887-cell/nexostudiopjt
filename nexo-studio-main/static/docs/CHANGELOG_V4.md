# Changelog — Nexo Studio v4

## Camada de segurança

- Criado o pacote interno `security/` para autorização, validação de JSON, rate limiting, validação de imagens, auditoria, cabeçalhos HTTP e checks de configuração.
- Centralizada a verificação de propriedade de negócio e objetos em operações CRUD selecionadas.
- Endurecido o endpoint público do chatbot com validação de método e Content-Type, limite de corpo JSON, validação de pergunta e rate limiting por IP/slug.
- Uploads de logo e imagem de destaque agora verificam tamanho, tipo declarado e formato real com Pillow; SVG não é aceito.
- Configurações de segredo, DEBUG, hosts e HTTPS podem ser ajustadas por variáveis de ambiente.
- Adicionado o item **Camada de segurança** à navegação da documentação acadêmica.
- Adicionada documentação Markdown detalhada com diagramas SVG embutidos, exemplos, limitações conhecidas e exercícios.
- Adicionados testes automatizados para validação da API, cabeçalhos e rate limiting, além dos testes existentes de isolamento entre empresas.

## Limitações

- Os testes Django não puderam ser executados neste ambiente de geração porque as dependências não puderam ser instaladas; a rede para o índice de pacotes estava indisponível. O código Python foi compilado sintaticamente com `compileall`, mas os testes devem ser executados no GitHub Codespaces antes da distribuição.
- O cache padrão é local e serve para demonstração em um único processo; produção exige cache compartilhado e proteção de borda.
- O projeto permanece educacional e não deve ser tratado como pronto para produção sem configuração e revisão independentes.
