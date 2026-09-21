# Portal web de estudos (Caderno de Inglês)

Página privada publicada como artifact do Claude: https://claude.ai/artifact/P9zMduKbR2gwH3jvURFawN

## O que entra e o que NUNCA entra

Entra só material de estudo: `INGLES.md` (seções de método), `TREINO-CHATGPT.md`, `drills/`, `vocabulario/`.
Nunca entram CONTEXTO, ROADMAP, FILA, APLICADAS nem `ativos/` (CVs e vagas). O `build_portal.py`
aborta se aparecer qualquer termo de jobhunt no pacote.

## Como atualizar depois de uma lição

1. Atualizar os `.md` (TRILHA-B2, REVISAO-GERAL etc.) como sempre.
2. `python portal/build_portal.py` → gera `portal/_out/portal.html` (valida escopo e sintaxe).
3. Republicar o artifact com `capabilities: {db: {}, user: {}}` (progresso privado por conta).
   Pedido pronto pra sessão: "atualiza o portal de inglês".

## Arquivos

- `build_portal.py` — lê os .md e monta a página.
- `portal-template.html` — a página (abas Hoje, Trilha, Revisão, Drills, Vocabulário, Método, Folhas).
- `_out/` — saída gerada, ignorada pelo git.

O progresso marcado no portal (dias de vocabulário, passadas dos drills) fica na conta do Rafael
(`data/users/<id>/progress`) e em cópia local no aparelho; o conteúdo dos .md continua sendo a fonte.
