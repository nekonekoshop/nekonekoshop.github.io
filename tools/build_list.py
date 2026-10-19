"""制作可能キャラ一覧のデータ（assets/data/chars.js）を ODS から作る。

使い方:  python tools/build_list.py
読むもの:
  D:\\AI物販\\アカウントキャラ分け.ods  … 「元」シート（F=作品, G=キャラ）
  D:\\AI物販\\いろいろ\\イラストリア.ods … 「キャラ」「ゲーム」「キャラリク」シート（B=作品, C=キャラ）
作品名の表記ゆれは ALIAS で統合、版権NG作品は NG で除外する。
"""
import datetime
import json
import re
import unicodedata
from pathlib import Path

import pandas as pd
import pykakasi

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "assets" / "data" / "chars.js"

ODS_ACCOUNT = r"D:\AI物販\アカウントキャラ分け.ods"
ODS_ILLUST = r"D:\AI物販\いろいろ\イラストリア.ods"

# 版権NG（00_共通ルール.md と同じ。追加するときは variant_rule.NG_WORKS にも足す）
NG = ["ウマ娘", "ホロライブ", "hololive", "ラブプラス", "フリーレン"]
# アカウントキャラ分け.ods「Sheet21」でリストから外すことになっているキャラ
NG_CHARS = ["橘ありす", "湊智花", "木之本桜", "チャチャ", "リィナ", "シャクティ",
            "スージィ", "スイートミント", "シェルファニール"]

# 表記ゆれ → 表示名
ALIAS = {
    "AIR": "AIR エアー", "Air": "AIR エアー",
    "Bastard バスタード": "BASTARD!! バスタード", "Bastard!!!": "BASTARD!! バスタード",
    "CLANNAD": "CLANNAD クラナド",
    "FF7": "FF7 ファイナルファンタジー7", "FF7 ファイナルファンタジー": "FF7 ファイナルファンタジー7",
    "Fate": "Fate フェイト",
    "Fate Grand Order FGO": "Fate/Grand Order FGO",
    "KOF": "KOF キング・オブ・ファイターズ", "KOF キングオブファイターズ": "KOF キング・オブ・ファイターズ",
    "Kanon": "Kanon カノン",
    "Re:ゼロから始める異世界生活": "Re:ゼロから始める異世界生活 リゼロ",
    "SSSS.GRIDMAN": "SSSS.GRIDMAN グリッドマン",
    "アイズ Is": "I\"s アイズ",
    "この素晴らしい世界に祝福を！": "この素晴らしい世界に祝福を！ このすば",
    "この素晴らしい世界に祝福を このすば": "この素晴らしい世界に祝福を！ このすば",
    "ぼっち・ざ・ろっく": "ぼっち・ざ・ろっく！",
    "まどかマギカ": "魔法少女まどか☆マギカ まどマギ", "まどかマギカ まどマギ": "魔法少女まどか☆マギカ まどマギ",
    "ようこそ スケベエルフの森へ": "ようこそ！スケベエルフの森へ",
    "きんぎょ注意報": "きんぎょ注意報！",
    "トップをねらえ": "トップをねらえ！",
    "YAT安心 宇宙旅行": "YAT安心！宇宙旅行",
    "ガンダムΖ": "ガンダム Z", "ガンダムΖΖ": "ガンダム ZZ", "機動武闘伝Gガンダム": "ガンダム G",
    "ガンダム": "ガンダム（その他シリーズ）",
    "センチメンタル ジャーニー グラフィティ": "センチメンタルグラフティ",
    "ソードアートオンライン": "ソードアート・オンライン SAO", "ソードアートオンライン SAO": "ソードアート・オンライン SAO",
    "デュープリズム Threads of Fate": "デュープリズム",
    "ドラクエ4": "ドラゴンクエスト ドラクエ",
    "ブリーチ": "BLEACH ブリーチ", "ブリーチ BLEACH": "BLEACH ブリーチ",
    "ホワイトアルバム": "WHITE ALBUM ホワイトアルバム", "WHITE ALBUM": "WHITE ALBUM ホワイトアルバム",
    "ヴァンパイア": "ヴァンパイア（ヴァンパイアセイヴァー）",
    "ヴァンパイアセイヴァー ハンター": "ヴァンパイア（ヴァンパイアセイヴァー）",
    "僕のヒーローアカデミア": "僕のヒーローアカデミア ヒロアカ",
    "ウイングマン": "夢戦士ウイングマン",
    "物語": "〈物語〉シリーズ", "物語 シリーズ": "〈物語〉シリーズ",
    "響け ユーフォニアム": "響け！ユーフォニアム", "響け!ユーフォニアム": "響け！ユーフォニアム",
    "超時空要塞マクロス": "マクロス",
    "ナルト": "NARUTO ナルト", "ナルト ボルト": "NARUTO ナルト",
    "東方Project": "東方Project",
    "‎楽園追放": "楽園追放",
    "NoeL Laneige ノエル": "NOëL ～La neige～ ノエル",
    "こち亀": "こちら葛飾区亀有公園前派出所 こち亀",
    "地獄先生ぬ～べ～ ぬーべー": "地獄先生ぬ〜べ〜",
    "ToHeart": "To Heart トゥハート",
}
# 先頭が英字の作品も、この読みで五十音順に並べたい場合に指定
YOMI = {
    "NARUTO ナルト": "なると", "BLEACH ブリーチ": "ぶりーち",
    # 読みの誤変換を直す
    "痕": "きずあと", "鬼滅の刃": "きめつのやいば", "原神": "げんしん", "鳴潮": "めいちょう",
}

kks = pykakasi.kakasi()


def hira(s):
    return "".join(x["hira"] for x in kks.convert(s))


def norm(s):
    s = unicodedata.normalize("NFKC", str(s)).lower()
    s = "".join(chr(ord(ch) - 0x60) if "ァ" <= ch <= "ヶ" else ch for ch in s)
    return re.sub(r"[\s・\-‐ー=＝!！?？:：\.〜~（）()\"'‎]", "", s)


def rows():
    acc = pd.read_excel(ODS_ACCOUNT, engine="odf", sheet_name=["元"], header=None)
    ill = pd.read_excel(ODS_ILLUST, engine="odf", sheet_name=["キャラ", "ゲーム", "キャラリク"], header=None)
    specs = [(acc["元"], 5, 6, None), (ill["キャラ"], 1, 2, 4), (ill["ゲーム"], 1, 2, 4), (ill["キャラリク"], 1, 2, 4)]
    for df, wc, cc, pc in specs:
        for i in range(len(df)):
            w, c = df.iat[i, wc], df.iat[i, cc]
            if pd.isna(w) or pd.isna(c):
                continue
            w, c = str(w).strip(), str(c).strip()
            if not w or not c or w in ("作品名", "作品") or c in ("キャラ", "キャラ名"):
                continue
            if pc is not None:
                p = df.iat[i, pc]
                if pd.isna(p) or str(p).strip() in ("", "-"):
                    continue  # プロンプトの無い行（メモ書き）は除外
            yield w, c


GROUPS = [("あ", "あいうえおぁぃぅぇぉゔ"), ("か", "かきくけこがぎぐげご"), ("さ", "さしすせそざじずぜぞ"),
          ("た", "たちつてとだぢづでどっ"), ("な", "なにぬねの"), ("は", "はひふへほばびぶべぼぱぴぷぺぽ"),
          ("ま", "まみむめも"), ("や", "やゆよゃゅょ"), ("ら", "らりるれろ"), ("わ", "わをん")]


def group_of(yomi):
    h = yomi[:1]
    for g, chars in GROUPS:
        if h in chars:
            return g
    return "英数"


def main():
    ng = [norm(x) for x in NG]
    ngc = [norm(x) for x in NG_CHARS]
    works = {}
    for w, c in rows():
        name = ALIAS.get(w, w)
        if any(x in norm(name) for x in ng):
            continue
        if any(norm(c) == x or norm(c).startswith(x) for x in ngc):
            continue
        key = norm(name)
        wk = works.setdefault(key, {"n": name, "c": {}})
        wk["c"].setdefault(norm(c), c)
    out = []
    for wk in works.values():
        n = wk["n"]
        latin = bool(re.match(r"[A-Za-z0-9〈]", n)) and n not in YOMI
        y = YOMI.get(n) or hira(re.sub(r"^[〈]", "", n))
        chars = sorted(wk["c"].values(), key=lambda s: hira(s))
        out.append({"n": n, "y": y, "g": "英数" if latin else group_of(y),
                    "c": [[ch, hira(ch)] for ch in chars]})
    order = {g: i for i, (g, _) in enumerate([("英数", "")] + GROUPS)}
    out.sort(key=lambda x: (order[x["g"]], x["n"].lower() if x["g"] == "英数" else x["y"]))
    data = {"updated": datetime.date.today().isoformat(), "works": out}
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text("window.CHAR_DATA=" + json.dumps(data, ensure_ascii=False, separators=(",", ":")) + ";\n",
                   encoding="utf-8")
    print(f"{len(out)} 作品 / {sum(len(x['c']) for x in out)} キャラ → {OUT}")


if __name__ == "__main__":
    main()
