# Testes de estresse dinâmico - teste de carga automatizada de especificações e gafanhotos do OpenAPI
<p align = "Center">
<a href = "https://locust.io/" Target = "_ Blank" rel = "Noopener Noreferrer">
)
</a>
</p>


Estrutura de teste de carga automatizada pronta para produção que gera testes abrangentes a partir de especificações do OpenAPI com recursos de segurança internos, validação e ferramentas de depuração.

## Conceito principal

Essa estrutura preenche a lacuna entre a documentação da API e a realidade do teste. Ao analisar as especificações do OpenAPI, ele cria automaticamente testes de carga realistas que evoluem com sua documentação da API. O princípio principal é manter o teste sincronizado com suas alterações na API - quando as atualizações do seu OpenAPI especifica, seus testes se adaptam automaticamente.

A estrutura enfatiza a segurança e a escala gradual, tornando -a adequada para testar ambientes de produção com confiança. Ele fornece informações abrangentes sobre o comportamento da API sob carga, mantendo controles rígidos de segurança.

Visão geral da arquitetura

`` `
OpenApi Spec → Testes gerados automaticamente → Teste de carga → Análise em tempo real
↓ ↓ ↓
Documentação de desempenho realista acionável
Cenários de sincronização Insights
`` `

## Recursos -chave

- ** Testes de gerações automáticas ** das especificações do OpenApi/Swagger
- ** Métodos de autenticação múltiplos ** (JWT, API Keys, OAuth, Auth Basic Auth)
- ** Padrões seguros de produção ** com validação abrangente
-** Monitoramento em tempo real ** com painel baseado na Web
- ** Depuração interativa ** e ferramentas de solução de problemas
- ** Cobertura de teste extensa ** com geração automatizada de cenários
- ** Pronto para o contêiner ** com orquestração completa do Docker
- ** Integração de CI/CD ** com relatórios detalhados

## Iniciar rápido

`` `BASH
faça configuração
# Editar .env com seus detalhes da API
fazer validar
Faça uma demonstração
`` `

Abrir http: // localhost: 8089 para acessar o painel de teste em tempo real.

## Documentação

- ** [Referência de comando] (doc/comands.md) ** - Documentação detalhada do comando com procedimentos e fluxos de teste
- ** [Guia de teste da API] (doc/api_testing.md) ** - Metodologia completa de teste e geração dinâmica de testes
- ** [Integração de CD/CD] (Doc/Cicd.md) ** - Implantação de produção com exemplos da AWS Fargate
- ** [Referência de parâmetros] (doc/parameters.md) ** - Guia de configuração completa
- ** [Guia do desenvolvedor] (Doc/Developer_guide.md) ** - Recursos de desenvolvimento avançado

## Configuração

A configuração básica requer configuração mínima:

`` `Env
OpenApi_url = https: //your-api.com/openapi.json
Base_url = https: //your-api.com
Auth_mode = nenhum
Max_users = 10
Spawn_rate = 2
`` `

Exemplos de autenticação:
`` `Env
# Token JWT
Auth_mode = JWT
Jwt_token = your.jwt.token.here

# Chave da API
Auth_mode = apikey
Api_key = your-api-chave

# Nome de usuário/senha
Auth_mode = login
Login_url =/auth/login
Login_user=user@example.com
Login_pass = senha
`` `

Recursos de segurança

A estrutura prioriza as práticas de teste seguras:

- Configurações padrão conservadoras para ambientes de produção
- Validação abrangente antes da execução do teste
- Limitação da taxa e proteção de recursos
- Filtragem de operação somente leitura
- Recomendações graduais de escala de carga
- Monitoramento em tempo real com alertas automáticos

## Uso da produção

Para ambientes de produção, a estrutura fornece:

1. ** Validação do ambiente de estadiamento ** - Teste de pré -produção abrangente
2. ** Escala de carga gradual **-A carga passo a passo aumenta
3. ** Monitoramento em tempo real ** - Métricas e alertas de desempenho ao vivo
4. ** Controles de segurança ** - Proteção automática contra configurações perigosas
5. ** Relatórios abrangentes ** - Análise detalhada para otimização de desempenho

## contribuindo

1. Fork o repositório
2. Crie um ramo de recursos
3. Faça suas alterações
4. Validação de execução: `Faça validar`
5. Envie uma solicitação de tração

## licença

MIT Licença - consulte o arquivo de licença para obter detalhes.

## Referências

- [Specificação OpenApi] (https://swagger.io/specification/) - Documentação oficial para padrões OpenAPI usados por esta estrutura
- [Documentação do Locust] (https://docs.locust.io/) - Documentação do mecanismo de teste de carga principal

----

** Estrutura de teste de carga pronta para produção projetada para segurança, confiabilidade e produtividade do desenvolvedor. **
