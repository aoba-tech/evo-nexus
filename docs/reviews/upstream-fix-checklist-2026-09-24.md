# Checklist de correções comunitárias para a `develop` do EvoNexus

Referência: `aoba-tech/evo-nexus:develop` em `fe15fd5`, idêntica à `evolution-foundation/evo-nexus:develop` na data desta análise (24/09/2026). Este documento identifica defeitos **do código-base atual**, antes de avaliar a adoção de funcionalidades novas. PR aberto, commit com título `fix` e arquivo de mesmo nome não comprovam aplicabilidade.

## Regra de entrada

- [ ] O comportamento defeituoso existe e pode ser demonstrado na `develop` atual, sem depender de uma funcionalidade exclusiva de um fork.
- [ ] O patch muda a causa do problema na upstream, e não apenas configuração, dados, branding ou infraestrutura particular de outro operador.
- [ ] Há teste de regressão ou reprodução antes/depois, incluindo o Hub Compose quando o patch toca Docker, rede ou autenticação.
- [ ] Dependências e alterações incidentais do histórico do fork foram excluídas. Para PR antigo contra `main`, selecionar o patch; não mesclar a branch inteira.
- [ ] A correção tem utilidade para nossa operação e não amplia privilégios sem necessidade.
- [ ] O revisor de segurança verificou exposição, credenciais, falha permissiva e rollback.

**Estados:** `CONFIRMADO` = evidência encontrada na `develop`; `REPRODUZIR` = componente existe, mas falta provar o defeito e/ou a adequação do patch; `EXCLUIR` = não corrige a baseline que usamos; `EM PR` = candidato isolado em draft, ainda sem testes de aceitação.

## 1. Correções com evidência direta na baseline

| Item | Defeito ou evidência na `develop` | Próxima checagem | Estado |
|---|---|---|---|
| [#81](https://github.com/evolution-foundation/evo-nexus/pull/81) watcher Brain Repo | `dashboard/backend/brain_repo/watcher.py` observa `brain_repo_dir`, destino do espelho, em vez de `install_dir`, origem das edições. | Editar arquivo na origem e observar sincronização. | EM PR [#2](https://github.com/aoba-tech/evo-nexus/pull/2) |
| [#127](https://github.com/evolution-foundation/evo-nexus/pull/127) espelho Brain Repo | `job_runner.py` usa `shutil.copytree(..., dirs_exist_ok=True)` sem reconciliar arquivos removidos da origem. | Testar exclusão comum, cancelamento, symlink e proteção contra exclusão em massa. | EM PR #2 |
| [#128](https://github.com/evolution-foundation/evo-nexus/pull/128) saída de rotinas | O scheduler usa `returncode`, mas rotinas do ADW podem terminar em código zero após falhas internas. | Forçar falha e verificar código final e registro da execução. | EM PR [#3](https://github.com/aoba-tech/evo-nexus/pull/3) |
| [#129](https://github.com/evolution-foundation/evo-nexus/pull/129) reload scheduler | O processo já tem reload via SIGHUP; patch aponta perda silenciosa de seções de YAML/configuração. | Alterar seção desconhecida e conferir arquivo antes/depois do reload. | EM PR #3 |
| [#100](https://github.com/evolution-foundation/evo-nexus/pull/100) Enter no chat | `AgentChat.tsx` chama `sendMessage()` no Enter sem condição de execução nessa ramificação. | Reproduzir envio enquanto agente ainda trabalha; selecionar patch sobre `develop`. PR fechado sem merge. | CONFIRMADO |
| [#99](https://github.com/evolution-foundation/evo-nexus/pull/99) WebSocket ocioso | `terminal_proxy.py` usa `client_ws.receive(timeout=30)` no proxy de sessão. | Manter sessão ociosa >30 s e testar retomada; considerar também #86. PR fechado sem merge. | CONFIRMADO |
| [#82](https://github.com/evolution-foundation/evo-nexus/pull/82) custo heartbeat | `heartbeat_runner.py` grava `cost_usd: None` e não registra tokens de entrada/saída do CLI neste fluxo. | Capturar saída real do provider e validar custo antes/depois; separar alterações de licença carregadas no histórico do PR. | CONFIRMADO |
| [#132](https://github.com/evolution-foundation/evo-nexus/pull/132) enabled heartbeat | `heartbeat_dispatcher.py` consulta `heartbeats.enabled` no banco; o PR aponta que editar YAML não atualiza esse valor. | Alterar YAML e consultar banco/execução; adaptar PR originalmente contra `main`. | REPRODUZIR |
| [#113](https://github.com/evolution-foundation/evo-nexus/pull/113) autenticação terminal | O proxy do terminal integra chat/terminal; a rota de WebSocket e a porta adicional exigem revisão de autenticação. | **Não usar o patch sem adaptação:** token vazio permite WS, `docker-compose.hub.yml` não acompanha bind em loopback, e `127.0.0.1` no forwardauth Traefik aponta para o próprio Traefik. Criar PR de segurança Hub/Swarm com testes. | CONFIRMADO; PATCH BLOQUEADO |

## 2. Defeito plausível em componente upstream: reproduzir antes de portar

| Fonte | Hipótese na baseline | Decisão necessária |
|---|---|---|
| [#77](https://github.com/evolution-foundation/evo-nexus/pull/77) restore Brain Repo | Fluxo de seleção pode exigir conexão antes de listar snapshots. | Fluxo real de restauração a partir de backup existente; patch isolado está em PR #2. |
| [#98](https://github.com/evolution-foundation/evo-nexus/pull/98) integridade backup | A cópia/scan atuais podem perder dados silenciosamente em casos de cancelamento e arquivos ignorados. | Casos de reprodução com dados descartáveis; conferir sobreposição com #127 antes de selecionar hunks. |
| [#83](https://github.com/evolution-foundation/evo-nexus/pull/83) exclusões Brain Repo | Arquivos de editor/ferramentas podem entrar no espelho. | Testar uma pasta concreta que existe em nosso workspace; verificar política de exclusão existente. |
| [#120](https://github.com/evolution-foundation/evo-nexus/pull/120) scanner | Padrões existentes podem gerar falso positivo/falso negativo. | Testar amostras sintéticas representativas; patch em PR #2 sem autoativação de licença. |
| [#86](https://github.com/evolution-foundation/evo-nexus/pull/86) chat/WS | Proxy e interface existem na baseline; PR fechado altera confiabilidade e dependências. | Reproduzir desconexão/rolagem, selecionar somente correções que ainda falham; `websocket-client` **já está declarado** em `pyproject.toml`. |
| [#102](https://github.com/evolution-foundation/evo-nexus/pull/102) lista de sessões | Terminal-server persiste índice de sessões; pode divergir dos logs após perda de cache. | Apagar somente índice em ambiente descartável e verificar recuperação. |
| [#124](https://github.com/evolution-foundation/evo-nexus/pull/124) alerta scheduler | Scheduler usa subprocessos; falta confirmar se falha é propagada/alertada após #128/#129. | Reproduzir rotina que falha e verificar alerta, sem duplicar correção. |
| [#130](https://github.com/evolution-foundation/evo-nexus/pull/130) agent tracker | Hook existe na upstream; PR afirma leitura de variável inexistente. | Executar evento real do hook e conferir tracking; patch isolado em PR #3. |
| [#133](https://github.com/evolution-foundation/evo-nexus/pull/133) URLs MCP | `.mcp.json` contém URLs de Gmail/Calendar. | Verificar endpoints oficiais atuais e conectividade antes de alterar. |
| [#134](https://github.com/evolution-foundation/evo-nexus/pull/134) heartbeat/tickets | Mecanismos de gatilho e tickets existem, mas o PR introduz janitor e semântica adicional. | Reproduzir timer inerte e ticket órfão em baseline, separar fix de funcionalidade. |
| [#131](https://github.com/evolution-foundation/evo-nexus/pull/131) Git/worktree Docker | **Git já está instalado** em `Dockerfile.swarm` e `Dockerfile.swarm.dashboard`; patch também inicializa repo em `/workspace`. | Reproduzir falha de worktree no container e verificar volumes/HEAD; não aceitar como simples instalação de Git. |
| [#135](https://github.com/evolution-foundation/evo-nexus/pull/135) terminal móvel | Chat e terminal existem; impacto é UX móvel. | Reproduzir em viewport móvel, prioridade baixa para o Hub atual. |

## 3. Commits exclusivos de fork que alteram componentes herdados

**Triagem, não aprovação.** Cada commit abaixo modifica um componente presente na upstream, mas ainda precisa de reprodução na `develop` e comparação do patch com a versão atual. Outros commits do fork, mesmo chamados `fix`, foram omitidos quando corrigem fluxos próprios (OpenReply, funil, editoriais, marca, OmniRoute, media-worker, etc.).

| Commit | Componente herdado | Prova antes de portar |
|---|---|---|
| [`sistemabritto:393c0e7`](https://github.com/sistemabritto/omni-nexus/commit/393c0e73) | Scheduler / buffer de logs | Executar rotina longa e confirmar atraso de stdout; testar `PYTHONUNBUFFERED`. |
| [`sistemabritto:d70964e`](https://github.com/sistemabritto/omni-nexus/commit/d70964e8) e [`97785b5`](https://github.com/sistemabritto/omni-nexus/commit/97785b55) | Scheduler / YAML e horário inválidos | Verificar se erro isolado derruba o processo; comparar com #129. |
| [`sistemabritto:4cd1e99`](https://github.com/sistemabritto/omni-nexus/commit/4cd1e997) | Brain Repo / caminho local após troca de máquina | Reproduzir reconexão/restore com volume novo; comparar com PR #2. |
| [`sistemabritto:abfcf3c`](https://github.com/sistemabritto/omni-nexus/commit/abfcf3cd), [`acf3e07`](https://github.com/sistemabritto/omni-nexus/commit/acf3e079) | Backup SQLite / restauração WAL | Testar snapshot consistente sob escrita e restore com WAL/SHM descartáveis. |
| [`sistemabritto:bf63d06`](https://github.com/sistemabritto/omni-nexus/commit/bf63d060) | Reconexão WebSocket chat/terminal | Reproduzir desconexão no Hub; comparar com #86/#99. |
| [`sistemabritto:afda74c`](https://github.com/sistemabritto/omni-nexus/commit/afda74ce) | Página de custos | Reproduzir entrada de custo de imagem sem total de tokens. |
| [`sistemabritto:8031b54`](https://github.com/sistemabritto/omni-nexus/commit/8031b54e) | Dockerfile / versão flutuante do provider | Checar versão atual e reprodutibilidade do build; pin implica política de atualização. |
| [`sistemabritto:b3f93b6`](https://github.com/sistemabritto/omni-nexus/commit/b3f93b6a) | Rota pública de compartilhamento | Verificar headers na resposta `/api/shares/<token>/view` e política para embed. |

## 4. Fora do checklist de correção da upstream atual

- [#125](https://github.com/evolution-foundation/evo-nexus/pull/125): Python 3.9; `pyproject.toml` exige Python >=3.10 e a imagem dashboard usa 3.12. Removido do PR #2.
- [#87](https://github.com/evolution-foundation/evo-nexus/pull/87): aumentar TTL de sessão de 24h para 90 dias é escolha de produto/segurança, não correção comprovada.
- [#74](https://github.com/evolution-foundation/evo-nexus/pull/74)/[#78](https://github.com/evolution-foundation/evo-nexus/pull/78)/[#79](https://github.com/evolution-foundation/evo-nexus/pull/79)/[#80](https://github.com/evolution-foundation/evo-nexus/pull/80): dedup/retry/DLQ no **Nexus** quando ele recebe webhook e chama EvoGo; avaliar só após confirmar esse fluxo e as garantias já oferecidas por EvoGo/Evolution API.
- [#111](https://github.com/evolution-foundation/evo-nexus/pull/111) Uptime Kuma e [#114](https://github.com/evolution-foundation/evo-nexus/pull/114) Portainer: skills de ferramentas externas; não corrigem defeito da upstream.
- [#121](https://github.com/evolution-foundation/evo-nexus/pull/121): OpenCode com numerosas mudanças adicionais; funcionalidade nova, não mesclar como fix da baseline.
- [#93](https://github.com/evolution-foundation/evo-nexus/pull/93) Todoist, [#122](https://github.com/evolution-foundation/evo-nexus/pull/122) Obsidian e integrações similares: considerar somente se o serviço faz parte do nosso fluxo.
- Commits do `sistemabritto/omni-nexus` para aplicações exclusivas daquele fork não entram neste checklist, ainda que alterem ocasionalmente arquivos compartilhados. Para os candidatos da seção 3, comparar o hunk e não apenas o nome do arquivo.

## Ordem de execução

1. [ ] Reproduzir #99/#100 e preparar patches isolados de chat/WS (problemas próximos do uso real do Hub).
2. [ ] Validar PR #2 com dados descartáveis, incluindo restauração e scanner; validar PR #3 com falhas induzidas. Nenhum está aprovado para merge ainda.
3. [ ] Criar correção específica para terminal/Hub/Swarm (#113), com autenticação WebSocket que falhe fechada e teste da porta 32352; manter fora dos PRs #2/#3.
4. [ ] Investigar #98, #82, #132/#134 e os commits de scheduler/backup do fork, com reprodução na baseline.
5. [ ] Reclassificar itens conforme resultados: `confirmado` → PR isolado → teste → revisão de segurança → merge.

## 5. Diagnóstico prioritário: painel de custos em zero ou vazio

A reclamação de custos sem valores tem **mais de uma causa possível** na `develop`:

- [ ] **API retorna zero cedo demais:** `dashboard/backend/routes/costs.py:18-25` retorna zero se `ADWs/logs/metrics.json` falta ou tem JSON inválido, **antes** de consultar `heartbeat_runs`. Reproduzir sem metrics.json e com uma linha de heartbeat de custo conhecido; corrigir a agregação para ler as fontes independentemente. Não localizamos PR comunitário que resolva esse caso.
- [ ] **Heartbeats gravam custo nulo:** `heartbeat_runner.py` atribui `cost_usd: None` à execução CLI. O [PR upstream #82](https://github.com/evolution-foundation/evo-nexus/pull/82) extrai `total_cost_usd` e tokens da saída JSON do Claude. Extrair apenas o patch do runner (o PR carrega alterações incidentais de licença/README), testar com saída real e variante inválida.
- [ ] **Página inteira quebra com entrada antiga de imagem:** `Costs.tsx` usa `e.token_usage.total_tokens` sem guarda. O [commit afda74ce](https://github.com/sistemabritto/omni-nexus/commit/afda74ce0dfceda473f54cb5ad2450f67f570a20) normaliza entradas antigas sem token_usage. Aplicar se houver erro JS/TypeError ou dados de imagem legados; ele não corrige totais zerados da API.
- [ ] **Custos de chat não entram no total:** `chat-bridge.js` recebe `total_cost_usd` e `usage`, mas `/api/costs` agrega apenas metrics.json de ADWs, heartbeat_runs e custos de imagens na UI. Confirmar expectativa de produto, persistência e fonte de custo do chat antes de abrir uma feature de contabilização. Não chamar isso de fix de renderização.
- [ ] **Estado da instalação:** conferir `/api/costs`, `/api/routines/image-costs`, presença/validade de `ADWs/logs/metrics.json`, uma linha de `heartbeat_runs` e erros do console. Isso separa dados ausentes de página quebrada sem expor chaves ou conteúdo de sessões.

**Prioridade:** reproduzir o retorno precoce e importar o fix do #82 em PR pequeno; o patch visual do fork é independente e só entra se a página estiver quebrando com entradas antigas.
