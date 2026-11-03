# Pestinha Anime — Registro de riscos (M0)

Severidade: P0 = bloqueia o alvo KDE/Wayland; P1 = degrada; P2 = menor. Todas as hipóteses estão **sem prova**
(ver `ANIME-WAYLAND-TEST-MATRIX.md`).

| ID | Sev | Risco | Impacto | Hipótese | Experimento | Mitigação |
|---|:-:|---|---|---|---|---|
| R1 | P0 | **PySide6 (wheel, Qt 6.11.3) × Qt do sistema Debian 13** | Plugin Wayland incompatível, aborts; `requirements.txt` já registra abort nativo no 6.12.0 | A wheel usa seu próprio Qt e plugins embarcados; conflitos surgem com Wayland/EGL/tema do sistema | M1-S1/B4: rodar com `QT_DEBUG_PLUGINS=1`; comparar wheel × `python3-pyside6` do Debian | Fixar versão; documentar caminho suportado |
| R2 | P0 | **Overlay e input region** | Pet bloqueia cliques ou não é clicável | Click-through hoje depende de pixel transparente (`body/pet.py`); sem `setMask` | S2/B6-B7: máscara pela silhueta, medir custo por quadro | Contrato de renderer devolve região opaca |
| R3 | P0 | **IPC KWin↔Python** | Sem janelas/posição → sem pouso | `callDBus()` chama, não expõe serviço; scripts não assinam sinais | S3/B17: serviço D-Bus Python + script que chama | Alt. sem script (Alt 1/2) e degradação graciosa |
| R4 | P0 | **DPI e multi-monitor** | Posição/tamanho errados entre telas | `scan_windows` usa o DPR só da tela primária (`app.py`); README admite pouco teste | S4/B12-B14 com escalas mistas | Conversão por tela; testes com geometrias simuladas |
| R5 | P0 | **Fullscreen e lockscreen** | Pet sobre vídeo/jogo ou sobre o bloqueio (privacidade) | Camada overlay pode ficar acima de fullscreen; lock pode ou não esconder | S5/B10-B11 | Política: esconder em fullscreen; nunca sobre lock |
| R6 | P1 | `move()` ineficaz em Wayland nativo | Pet não anda | xdg-toplevel não permite posição do cliente | B3 | Superfície por monitor com posição interna |
| R7 | P1 | Leitura de janelas/ocioso indisponível | Menos sentidos; SNN recebe entradas padrão | `linux.py` só X11 | B17 | Capability Layer com "não suportado" explícito |
| R8 | P1 | Atalho global em Wayland | Pânico inacessível | `pynput` não funciona; portal pode exigir confirmação | B16 | Pânico também via bandeja (já existe) + portal |
| R9 | P1 | Privacidade do script KWin | Script com acesso amplo | Qualquer script pode chamar D-Bus arbitrário | B18 | Payload mínimo (retângulos), auditável |
| R10 | P1 | Arte × contrato de estados | Retrabalho de assets | Mapeamento `emotion`→sprite imaturo | Revisão em M3 | Arte final só em M5 |
| R11 | P1 | Regressão da SNN | Perda de personalidade/memória | Mudança em `core/` ou `memory/` | Testes existentes (352) + diff vazio em `core/` | Fronteira `PetState`/`Body`; sem migração |
| R12 | P2 | CI só offscreen | Falsa confiança | `conftest.py` força offscreen | Execução manual em KDE | Matriz com PASS apenas por evidência real |
| R13 | P2 | Documentação externa não verificada | Decisões erradas | Sites oficiais inacessíveis nesta sessão | Reconferir no M1 | Marcar tudo como hipótese |
| R14 | P2 | Plano normativo ausente | Divergência de escopo | `PLANO-PESTINHA-ANIME-v1.1.md` não fornecido | Receber o arquivo | Reconciliar documentos |
