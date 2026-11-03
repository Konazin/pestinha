# Semântica da região de entrada (input region) e limites dos experimentos de máscara

> **Status: nota técnica de preparação. Nenhum comportamento descrito como "Qt faz X em Wayland" foi
> verificado.** As afirmações sobre o protocolo vêm de conhecimento prévio e as referências oficiais não puderam
> ser abertas nesta sessão (ver `docs/adr/002-kde-wayland-backend.md` § Referências). Tudo marcado **[H]** é hipótese a
> confirmar em KDE Wayland real. Nenhum resultado de teste está registrado aqui.

## 1. Quatro coisas que NÃO são a mesma

| Conceito | O que controla | Onde aparece nas sondas |
|---|---|---|
| **Transparência visual** (alfa dos pixels, `WA_TranslucentBackground`) | Como a superfície **aparece** | `--tinta 0` (véu invisível) |
| **Máscara Qt** (`QWidget.setMask` / `clearMask`) | Para o Qt: "partes visíveis" do widget. Se e como vira entrada no compositor é **[H]** | `mask-central`, `mask-minima`, `mask-vazia-qt`, `mask-removida`, `dinamica` |
| **Input region Wayland** (`wl_surface.set_input_region`) | Quem **recebe** o ponteiro, definida pelo cliente por superfície | Só observável via `WAYLAND_DEBUG` (§5) |
| **`Qt.WindowTransparentForInput`** | Flag do Qt para "não receber entrada". Mapeamento para uma região de entrada vazia no Wayland é **[H]** | `transparente-input` |

## 2. Semântica do protocolo Wayland (de memória; reconfirmar na especificação)

- O valor inicial da região de entrada é **infinito** (a superfície inteira aceita entrada).
- `set_input_region(nil)` (região **nula**) devolve a região ao valor **infinito**.
- Uma `wl_region` criada **sem nenhum retângulo** é uma região **vazia**: a superfície **não recebe** entrada.
- A região tem semântica de cópia e só vale após `wl_surface.commit`.
- Coordenadas em espaço local da superfície (lógicas, não pixels físicos).

Consequência: **"nula" e "vazia" são opostas** (entrada total × nenhuma entrada). Qualquer camada que converta
uma região **vazia** do Qt em `nil` inverte a intenção.

## 3. O que o Qt faz com isso **[H]**

- Se `setMask(QRegion())` (vazia) vira `set_input_region(nil)`, o resultado é **entrada total**, equivalente a
  "sem máscara" — a armadilha que o experimento `mask-vazia-qt` investiga.
- Se vira uma `wl_region` sem retângulos, o resultado é **nenhuma entrada**.
- A máscara pode afetar só a entrada, só o visual, ambos ou nenhum no backend Wayland; no X11 (`xcb`), `setMask`
  usa o modelo de formas do X (afeta o desenho e a entrada). Todos **[H]**.
- Escala de tela (DPR) pode alterar as coordenadas enviadas; atualização e `commit` podem ter atraso.

## 4. Fato observado no lado Qt (teste de fumaça `offscreen` no contêiner; não é Wayland)

`QWidget.mask().isEmpty()` retornou **`True` nos três casos**: nenhuma máscara aplicada, após `setMask(QRegion())` e
após `clearMask()`. **Portanto o estado Qt não distingue "máscara vazia" de "máscara removida"**, e o campo
`qt_mask_isEmpty` do log **não prova** o que foi enviado ao compositor. Para uma máscara não vazia, o
`boundingRect` é fiel (ex.: `[220,120,160,160]`, `[0,0,1,1]`). Esse fato é sobre a API do `QWidget`; o que
o plugin Wayland transmite continua **[H]**.

## 5. Como cada variante deve ser lida

| Variante (`--regiao`) | Intenção | O que o resultado **pode** indicar | O que **não** prova |
|---|---|---|---|
| `nenhuma` | Linha de base: sem máscara | Se superfície translúcida captura cliques sem máscara (T17/T18) | Nada sobre máscara |
| `mask-central` | Região **não vazia** = quadrado | Se uma região positiva restringe a entrada (T20) | Que a região do compositor seja exatamente a do Qt |
| `mask-minima` | Região **não vazia, quase nula** (1×1 px no canto) | **Controle confiável de "quase nenhuma entrada"** sem o problema vazia×nula (T42) | — |
| `mask-vazia-qt` | Região Qt **vazia** | **Classificar** (T19): (a) a sonda recebe cliques ⇒ consistente com o Qt tratar como "sem máscara"; (b) nenhum clique recebido e os cliques passam ⇒ consistente com entrada vazia efetiva, **a confirmar por T43** | **Não** é o teste de "input region Wayland vazia". Resultado a priori indeterminado |
| `mask-removida` | Controle: máscara aplicada e depois `clearMask()` | Se remover a máscara restaura a entrada total (T41) | — |
| `transparente-input` | Candidata a "entrada vazia" pela flag do Qt | Se o Qt/compositor honram a flag (T21) | Qual região foi enviada (use T43) |
| `dinamica` | Custo e correção de atualizar a máscara a ~60 Hz | `setMask_ms` (média, p95, máx.) e se o clique acompanha | Atraso no compositor (só o tempo de chamada local é medido) |

### Evidência objetiva do que o Qt enviou (T43)
```bash
WAYLAND_DEBUG=client timeout --signal=INT 30 python3 sonda_janela.py --plataforma wayland \
    --modo regiao --regiao mask-vazia-qt --grande --tempo 20 2> out/wayland-debug-mask-vazia.log
./extrair_input_region.sh out/wayland-debug-mask-vazia.log
```
Procure `set_input_region(nil)` (entrada infinita) × `set_input_region(wl_region@N)` (região definida) e, para
`wl_region@N`, as chamadas `.add(...)`. Uma `wl_region` sem `.add` é região vazia. O formato exato das linhas
depende da versão do libwayland **[H]**. O log pode conter tráfego de protocolo: revise antes de compartilhar.

## 6. Limitações do teste (declaradas)

1. O cliente **não consegue ler** a input region efetiva do compositor; só vê o que enviou (via `WAYLAND_DEBUG`) e
   o efeito dos cliques.
2. A contagem de cliques mede apenas o que **chega à sonda**; o "passou para baixo" depende da resposta do operador
   e da janela escolhida embaixo.
3. Cliques em bordas, áreas anti-aliased e com escala fracionária podem se comportar diferente das áreas internas.
4. O KWin pode ter tratamento próprio (ex.: regras, efeitos) que não é separável pela sonda.
5. Resultados em `offscreen`/Xvfb/CI não valem. Esta nota **não registra resultado algum**.

## 7. Regra de leitura (o que é permitido concluir)

| Cliques recebidos pela sonda fora do alvo | Operador: cliques fora chegaram embaixo | `WAYLAND_DEBUG` | Conclusão permitida |
|---|---|---|---|
| > 0 | não | qualquer | A entrada **não** estava restrita nessa fase |
| 0 | sim | mostra região vazia ou restrita ao alvo | Consistente com região de entrada efetiva; ainda é **uma** observação, não uma garantia geral |
| 0 | sim | sem log | Consistente, **mas não explica por quê**; registrar como "sem evidência de protocolo" |
| 0 | não | qualquer | Indeterminado (clique não chegou a lugar nenhum: reexecutar) |

Em todos os casos o registro na matriz é `PASS`/`FAIL` **somente** conforme os critérios de `MATRIZ-M1.md`.
