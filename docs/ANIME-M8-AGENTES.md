# M8 — Integração com agentes de programação (planejamento futuro)

> **Status: planejamento pós-MVP. NÃO implementar agora.** Nada aqui foi construído, testado ou verificado contra
> as interfaces reais dos agentes. Origem: mensagem do proprietário (roadmap v1.2); não há arquivo de plano para
> conferir. Autorização: pendente e posterior ao MVP.

## Objetivo

A personagem reage ao estado de agentes de programação rodando localmente, sem ler o que eles fazem.

Agentes-alvo: **Claude Code**, **OpenAI Codex CLI** e **Google Antigravity/AGY** (este último *sujeito à
verificação das interfaces disponíveis*).

Estados que a personagem poderá refletir: `sessão iniciada`, `agente trabalhando`, `aguardando aprovação`,
`executando testes`, `tarefa concluída`, `erro`.

## Requisitos aprovados

1. Adaptadores **independentes** por agente.
2. Eventos **padronizados**.
3. Comunicação **local**.
4. Compatível com **agentes simultâneos**.
5. **Nenhuma leitura** de prompts, código-fonte ou dados privados por padrão.
6. **Nenhuma execução automática** de comandos nem aprovação de ações.
7. Offline por padrão (D8).

## Arquitetura proposta (PROPOSTA, a validar)

```text
agente (Claude Code / Codex CLI / AGY)
   └─ mecanismo de notificação do próprio agente (hook, notify, ...)   ← a verificar por agente
        └─ adaptador do agente (processo/script pequeno, 1 por agente)
             └─ filtra para o evento padrão e DESCARTA todo o resto
                  └─ canal local (ex.: socket Unix em $XDG_RUNTIME_DIR, modo 0600; sem porta de rede)
                       └─ receptor no Pestinha → agregador de sessões → estado exibido
```

### Evento padrão (rascunho)

| Campo | Conteúdo | Observação |
|---|---|---|
| `v` | versão do esquema | |
| `agent` | `claude-code` \| `codex-cli` \| `agy` | enumeração fechada |
| `session` | identificador opaco (hash local) | nunca caminho, nome de projeto ou prompt |
| `state` | `session_started` \| `working` \| `awaiting_approval` \| `running_tests` \| `done` \| `error` | enumeração fechada |
| `ts` | instante do evento | |

Campos fora dessa lista são **rejeitados** pelo receptor (lista de permissão). Nada de texto livre, caminhos,
comandos, trechos de código ou mensagens de erro.

### Múltiplos agentes
Agregação por prioridade proposta: `awaiting_approval` > `error` > `running_tests` > `working` > `done` >
`session_started`; sessões expiram por tempo sem eventos. Detalhes a definir em M8.

## Fronteiras com o que já existe (fatos do repositório)

- `pestinha/sense/senses.py` já classifica os nomes de processo `claude` e `codex` como `PROGRAMMING`
  (`ACTIVITY_APPS`). Isso é só o **nome do programa em primeiro plano** e não indica estado do agente.
- Novos sinais entrariam como canal sensorial (`SENSORY_SPEC` em `pestinha/core/nervous_system.py`), o que
  **altera a SNN**. Pela decisão D4, isso exige aprovação própria. **Alternativa proposta:** mapear os estados
  só para `PetState`/animação (camada de apresentação), sem tocar em `core/`. Escolha pendente.

## Itens a verificar antes de qualquer implementação (nenhum foi verificado)

| Item | Pergunta | Status |
|---|---|---|
| Claude Code | Quais eventos de hook existem e que dados cada um entrega? Há campo com prompt/código que o adaptador precisa descartar? | NOT VERIFIED |
| Codex CLI | Existe mecanismo de notificação por evento? Que granularidade (início, aprovação, fim, erro)? | NOT VERIFIED |
| Antigravity/AGY | Existe interface local utilizável (CLI, hooks, logs, API)? | NOT VERIFIED — pode não existir |
| "Executando testes" | Algum agente informa isso sem inspecionar comandos? Se não, o estado pode ficar indisponível | NOT VERIFIED |
| "Aguardando aprovação" | Há sinal confiável? Esse estado é **só visual**: a personagem nunca aprova nem recusa | NOT VERIFIED |
| Estabilidade das interfaces | Versões e mudanças entre releases | NOT VERIFIED |

## Fora de escopo (permanente, salvo decisão explícita do proprietário)

Ler prompts, respostas, código, diffs, caminhos ou saída de comandos; enviar teclas ou entrada ao agente;
aprovar, recusar ou executar qualquer ação; rede externa; telemetria; screenshots.

## Riscos

Ver `ANIME-RISK-REGISTER.md` (R15–R18). Critérios de teste serão escritos quando o M8 for autorizado.
