# `lancadores/` — formas opcionais de iniciar o app

Não fazem parte do pacote `pestinha/`; nada nele depende desta pasta. Só usam a biblioteca padrão do Python.

| Arquivo | O que faz |
|---|---|
| `pestinha_xwayland.py` | Linux: inicia `main.py` com `QT_QPA_PLATFORM=xcb` (XWayland), só no processo filho. |

```bash
python lancadores/pestinha_xwayland.py --simular          # mostra o comando, sem abrir o app
python lancadores/pestinha_xwayland.py --direto           # demais argumentos vão para o main.py
```

Use o Python do venv do projeto (o launcher executa o `main.py` com o mesmo interpretador).
Recusa (código 2) fora do Linux e quando `DISPLAY` está vazio. Não altera a sessão KDE nem o ambiente global.
Decisão e limitações: [`docs/adr/003-xwayland-backend-provisorio.md`](../docs/adr/003-xwayland-backend-provisorio.md).
