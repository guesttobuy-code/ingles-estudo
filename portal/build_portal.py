"""Monta o portal web de estudos de inglês (artifact) a partir deste repo.

Uso:  python portal/build_portal.py   ->   portal/_out/portal.html  (não versionado)

Lê SOMENTE material de estudo: INGLES.md (seções de método), TREINO-CHATGPT.md,
drills/*.md e vocabulario/*.md. Nunca lê CONTEXTO, ROADMAP, FILA, APLICADAS nem ativos/.
"""
import re, json, pathlib, datetime, sys

HERE = pathlib.Path(__file__).resolve().parent
R = HERE.parent
OUT_DIR = HERE / "_out"
OUT_DIR.mkdir(exist_ok=True)


def read(rel):
    return (R / rel).read_text(encoding="utf-8").replace("\r\n", "\n")


# ---------- documentos de estudo ----------
docs = {
    "trilha": read("drills/TRILHA-B2.md"),
    "revisao": read("drills/REVISAO-GERAL.md"),
}

# INGLES.md: só as seções de método de estudo (sem cabeçalho pessoal, sem trackers em branco)
ing = read("INGLES.md")
parts = re.split(r"(?m)^(?=## )", ing)
keep = []
for p in parts:
    if re.match(r"## (Diagnóstico|Rotina diária|Progressão por fase|Agenda diária concreta|Vocabulário de alta frequência)", p):
        if p.startswith("## Vocabulário de alta frequência"):
            p = p.split("**Tracker de progresso**")[0].rstrip() + "\n"
        keep.append(p.rstrip() + "\n")
docs["metodo"] = "# Método de estudo\n\n" + "\n".join(keep)

chat = read("TREINO-CHATGPT.md")
docs["chatgpt"] = chat.split("\n---\n", 1)[1].strip()

# ---------- drills ----------
drills = []
for name in ["FASE-0", "FASE-1", "FASE-2", "FASE-3", "FASE-4", "EXTRA-IT"]:
    md = read(f"drills/{name}.md")
    drills.append({"id": name, "title": md.splitlines()[0].lstrip("# ").strip(), "md": md})

# ---------- vocabulário ----------
E1 = re.compile(r"^\*\*(.+?)\*\*\s+\*\((.+?)\)\*\s+—\s+(.+)$")
E2 = re.compile(r"^\*(.+?)\*\s+→\s+(.+)$")
ORDER = ["A1", "A2", "B1", "B2", "B2+", "C1"]


def parse_slice(path):
    sid = path.stem
    level = re.match(r"([ABC][12]\+?)-", sid).group(1)
    lines = path.read_text(encoding="utf-8").replace("\r\n", "\n").splitlines()
    title = lines[0].lstrip("# ").strip()
    rng = re.search(r"\((.+)\)\s*$", title)
    days, cur = [], None
    i = 0
    while i < len(lines):
        ln = lines[i].rstrip()
        if ln.startswith("## "):
            cur = {"label": ln[3:].strip(), "entries": []}
            days.append(cur)
        elif ln.startswith("---"):
            cur = None
        elif cur is not None and ln.startswith("**") and not ln.startswith("**Fechou"):
            m = E1.match(ln)
            if not m:
                sys.exit(f"{sid}: linha de palavra não reconhecida: {ln!r}")
            j = i + 1
            while j < len(lines) and not lines[j].strip():
                j += 1
            m2 = E2.match(lines[j].strip())
            if not m2:
                sys.exit(f"{sid}: frase não reconhecida após {m.group(1)!r}: {lines[j]!r}")
            cur["entries"].append({"w": m.group(1), "pos": m.group(2), "tr": m.group(3),
                                   "en": m2.group(1), "pt": m2.group(2)})
            i = j
        i += 1
    return {"id": sid, "level": level, "range": rng.group(1) if rng else "", "days": days}


files = [p for p in (R / "vocabulario").glob("*.md") if p.stem != "INDICE"]
vocab = [parse_slice(p) for p in files]
vocab.sort(key=lambda s: (ORDER.index(s["level"]), int(s["id"].split("-")[1])))

total = sum(len(d["entries"]) for s in vocab for d in s["days"])
print("fatias:", len(vocab), "| palavras:", total)
assert len(vocab) == 54, "esperava 54 fatias"
assert total == 5232, f"esperava 5232 palavras, achei {total}"

data = {
    "built": datetime.date.today().strftime("%d/%m/%Y"),
    "docs": docs,
    "drills": drills,
    "vocab": vocab,
}

tpl = (HERE / "portal-template.html").read_text(encoding="utf-8")
blob = json.dumps(data, ensure_ascii=False).replace("</", "<\\/").replace("<!--", "<\\!--")
out = tpl.replace("__DATA__", blob)
(OUT_DIR / "portal.html").write_text(out, encoding="utf-8")
print("portal.html:", round(len(out.encode("utf-8")) / 1024), "KB")

# guarda de escopo: nada de jobhunt no que vai pra web
banned = ["APLICADAS", "FILA.md", "ROADMAP", "CONTEXTO", "Futureproofing", "R$", "CNPJ", "CV v6"]
hits = [b for b in banned if b in blob]
print("termos de jobhunt no pacote:", hits or "nenhum")
if hits:
    sys.exit("ABORTADO: termos de jobhunt no pacote — revisar antes de publicar")

# guarda de sintaxe: o script da página tem que passar no node --check
import shutil, subprocess
scripts = re.findall(r'<script(?![^>]*\bsrc=)(?![^>]*application/json)[^>]*>(.*?)</script>', out, re.S)
node = shutil.which("node")
if node and scripts:
    chk = OUT_DIR / "check.js"
    chk.write_text(scripts[-1], encoding="utf-8")
    r = subprocess.run([node, "--check", str(chk)], capture_output=True, text=True)
    print("node --check:", "OK" if r.returncode == 0 else r.stderr[:300])
    if r.returncode != 0:
        sys.exit("ABORTADO: erro de sintaxe no JavaScript da página")
    chk.unlink()
