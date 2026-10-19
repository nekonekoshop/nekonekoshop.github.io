"""index.html のアイコン・ロゴ（<!--SPRITE-->〜<!--/SPRITE-->）を list.html にコピーする。"""
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
src = (ROOT / "index.html").read_text(encoding="utf-8")
block = re.search(r"<!--SPRITE-->.*?<!--/SPRITE-->", src, re.S).group(0)
for name in ["list.html"]:
    p = ROOT / name
    t = p.read_text(encoding="utf-8")
    t = re.sub(r"<!--SPRITE-->(.*?<!--/SPRITE-->)?", lambda m: block, t, count=1, flags=re.S)
    p.write_text(t, encoding="utf-8")
    print("synced", name)
