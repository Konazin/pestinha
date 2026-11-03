# Runbook M1 — diagnóstico no Debian 13 + KDE Plasma 6 + Wayland

Execute **na sessão gráfica do KDE Wayland real** (não via SSH sem display, não em VM sem aceleração se puder
evitar, não em Xvfb). Tempo estimado: 60–90 min. Registre tudo em [`MATRIZ-M1.md`](MATRIZ-M1.md).

## 0. Segurança e privacidade (leia antes)

- Janelas de teste são transparentes e podem **bloquear cliques** abaixo delas até fechar. Todas fecham
  sozinhas (`--tempo`) e há um vigia que força a saída. Use sempre o prefixo `timeout --signal=INT N`.
- Saída de emergência, se o mouse ficar preso: aguarde o tempo; ou `Alt+Tab`/teclado; ou outra TTY
  (`Ctrl+Alt+F3`) e `pkill -f sonda_`.
- Os scripts gravam em `diagnostico/m1/out/` (ignorado pelo git). **Revise antes de compartilhar**: o relatório
  não deve conter títulos de janelas, caminhos pessoais nem conteúdo. O console de depuração do KWin e o
  `journalctl` podem mostrar títulos: use só para olhar localmente.
- O Pestinha original (S1) registra o atalho global via `pynput` e lê o **nome** do programa ativo; roda numa
  **cópia temporária** (não toca no seu `memory/`).
- **REQUER AUTORIZAÇÃO (não faça agora):** carregar qualquer script no KWin, criar regras de janela, instalar
  pacotes do sistema, suspender a máquina (opcional T32).

## 1. Preparação

```bash
git clone https://github.com/Konazin/pestinha.git && cd pestinha
git checkout claude/pestinha-anime-m1-prep      # ou o main, após o merge
python3 -m venv ~/.venvs/pestinha-m1 && source ~/.venvs/pestinha-m1/bin/activate
pip install "PySide6==6.11.3" psutil numpy pynput   # mesmas versões de requirements.txt; não altera o repositório
cd diagnostico/m1
```

Dependências de sistema que **podem** faltar (confirme pelo log do Qt, não instale às cegas):
`libegl1`, `libxkbcommon0`, `libxcb-cursor0` (plugin `xcb` do Qt ≥ 6.5), `xwayland`. Opcional e **decisão sua**:
`wayland-utils` (comando `wayland-info`, usado em T35/T36). Sem ele, os testes correspondentes ficam `NOT TESTED`.

## 2. Execução em ordem

Cada bloco indica a investigação (Inv.), o teste da matriz e o que observar.

### 2.1 Ambiente e identidade da sessão — Inv. 6, 9, 10 — T01, T24, T33, T35, T36, T39
```bash
./coletar_ambiente.sh
./verificar_kwin_dbus.sh
./verificar_layershell.sh
```
Confirme em `ambiente.txt`: `XDG_SESSION_TYPE=wayland` e um processo `kwin_wayland`. **Se não for KDE
Wayland real, pare: os resultados são inválidos.** Registre também as escalas por monitor (`kscreen-doctor -o`).

### 2.2 Compatibilidade PySide6 × Qt — Inv. 6 — T02–T04
```bash
python3 sondar_qt.py --plataformas xcb wayland
```
Veja `qt.json`: `codigo_saida` 0 e `platformName` de cada plataforma; `bibliotecas_carregadas` (todas as `libQt6*`
devem vir de **um único prefixo**: wheel ou sistema, nunca misturados); `qt_debug_plugins_*.log` explica
falhas de plugin.

### 2.3 Pestinha original (S1) — Inv. 1, 2 — T06–T09, T40
```bash
./rodar_pestinha_original.sh xcb 90
./rodar_pestinha_original.sh wayland 90
```
Observe: o pet aparece? anda (move) sozinho? fica por cima? clica/arrasta? Anote cada observação na matriz.
Falha de inicialização (abort, plugin) também é resultado — guarde `pestinha.stderr.log`.

### 2.4 Posicionamento de janelas Qt — Inv. 3 — T10–T14
Abra um editor de texto ao lado para ter um "programa de baixo". Para cada linha, observe a janela azul-clara e
responda `s/n/nt` às perguntas do final.
```bash
timeout --signal=INT 40 python3 sonda_janela.py --plataforma xcb     --modo mover --api move
timeout --signal=INT 40 python3 sonda_janela.py --plataforma wayland --modo mover --api move
timeout --signal=INT 40 python3 sonda_janela.py --plataforma wayland --modo mover --api setGeometry
timeout --signal=INT 40 python3 sonda_janela.py --plataforma wayland --modo mover --api janela
timeout --signal=INT 40 python3 sonda_janela.py --plataforma wayland --modo mover --api move --flags normal
```
O campo `erro_autorrelato` mostra o que o Qt **diz** ter aplicado; em Wayland isso **não prova** nada. A prova é
"a janela mudou visivelmente de lugar" (resposta do operador). Corroboração opcional: o console de depuração
do KWin mostra a geometria real (somente para olhar; não copie títulos).

### 2.5 Transparência, click-through e região de entrada — Inv. 4, 5 — T15–T23
**Transparência visual ≠ passagem de clique.** Use primeiro a janela pequena, depois a grande (`--grande`
cobre a área disponível do monitor; fecha em `--tempo`). Durante a execução, **clique** em ícones/janelas
embaixo, **fora** do quadrado vermelho, ~20 vezes, e ~20 vezes **dentro** dele. Os contadores aparecem no quadrado
e ficam em `eventos.jsonl` (`clique_recebido`).
```bash
# janela pequena
timeout --signal=INT 45 python3 sonda_janela.py --plataforma wayland --modo regiao --regiao nenhuma --tempo 35
# superfície grande (CUIDADO: pode bloquear cliques até fechar)
timeout --signal=INT 30 python3 sonda_janela.py --plataforma wayland --modo regiao --regiao nenhuma           --grande --tempo 20
timeout --signal=INT 30 python3 sonda_janela.py --plataforma wayland --modo regiao --regiao mask-vazia        --grande --tempo 20
timeout --signal=INT 30 python3 sonda_janela.py --plataforma wayland --modo regiao --regiao mask-central      --grande --tempo 20
timeout --signal=INT 30 python3 sonda_janela.py --plataforma wayland --modo regiao --regiao transparente-input --grande --tempo 20
timeout --signal=INT 40 python3 sonda_janela.py --plataforma wayland --modo regiao --regiao dinamica         --grande --tempo 30
# comparação com XWayland
timeout --signal=INT 30 python3 sonda_janela.py --plataforma xcb --modo regiao --regiao nenhuma   --grande --tempo 20
timeout --signal=INT 30 python3 sonda_janela.py --plataforma xcb --modo regiao --regiao mask-vazia --grande --tempo 20
```
Para transparência pura use `--tinta 0` (sem véu): o objetivo é ver se pixels totalmente transparentes deixam o
clique passar. Em `dinamica`, `resumo.json` traz `setMask_ms` (média, p95, máx.): orçamento de quadro = 16 ms.

### 2.6 Monitores e escalas — Inv. 9 — T24–T27
Com 2 monitores, nas combinações 100%/100%, 100%/150% e uma escala fracionária (ex.: 125% ou 175%), em
Configurações do Sistema → Tela (**mudar a escala é ação sua**; os scripts não alteram nada):
```bash
timeout --signal=INT 70 python3 sonda_janela.py --plataforma wayland --modo mover --caminho telas --passos 9 --tempo 60
```
Anote: a janela passou de um monitor para o outro? tamanho coerente? nitidez? o clique acompanha?

### 2.7 Fullscreen, foco, bloqueio — Inv. 10 — T28–T32
```bash
python3 sonda_ciclo.py --plataforma wayland --tempo 240
```
Durante os 4 min: abrir um vídeo/app em tela cheia; `Meta+L` e desbloquear; digitar ~20 caracteres num editor
(nenhum pode se perder); alternar janelas. (T32, opcional: suspender e retomar.) Responda às perguntas finais.

### 2.8 KWin Scripting e LayerShellQt — Inv. 7, 8 — T33–T38
Somente leitura: já coletado em 2.1 (`kwin-dbus.txt`, `layershell.txt`). Registre o que existe (métodos de
`/Scripting`, layer-shell anunciado, pacote `liblayershellqtinterface*`, plugin de shell na wheel/sistema,
*binding* Python). **O IPC KWin↔Python (T34) não é testado sem autorização expressa**; quando houver, será um
script KWin separado e revisado (S3, M1 fase seguinte).

## 3. Coleta de logs
```bash
./empacotar_resultados.sh                 # só os arquivos de out/ (sem journal)
./empacotar_resultados.sh --com-journal   # inclui linhas filtradas (kwin/plasma/Qt/wayland) dos últimos 30 min
```
Revise o `.tar.gz`/`out/` (e remova o que não quiser compartilhar) antes de enviar. Para depurar o Qt, os scripts já
usam `QT_DEBUG_PLUGINS=1`; para detalhe extra de protocolo Wayland (muito verboso, manual):
`WAYLAND_DEBUG=1 python3 sonda_janela.py ... 2> wayland-debug.log` (contém tráfego de protocolo; revisar).

## 4. Relatório
Preencha a coluna "Resultado" da matriz (`PASS`/`FAIL`/`NOT TESTED`) com o nome do arquivo de evidência.
Regras: sessão não-KDE-Wayland ⇒ `NOT TESTED` (inválido); falta de recurso/permissão ⇒ `NOT TESTED` com motivo;
`PASS` só com evidência (log + observação). Não declare o M1 aprovado: isso é decisão do proprietário (ver
[`CRITERIOS-APROVACAO.md`](CRITERIOS-APROVACAO.md)).

## 5. Limitações conhecidas das sondas
- O autorrelato de posição em Wayland é o pedido do Qt, não a posição real (por isso a observação humana).
- `setMask()` do `QWidget` → região de entrada Wayland é **hipótese** a confirmar (T20–T22).
- As sondas medem sua própria janela; não observam o Pestinha real em movimento contínuo (isso é T07/T09/T40).
- Escalas fracionárias dependem de `wp_fractional_scale` e do Qt; o comportamento é o que se mede.
