# img2svg

画像をSVGへ変換するための実験・ツールリポジトリ。

## DTPXの文脈

DTPXではSVGを単なる「画像形式」ではなく、**編集工程と出力工程をつなぐ中間表現**として捉える。

```
企画
 ↓
editor-agent
 ↓
structured text
 ↓
DTPX
 ↓
SVG / PDF / EPUB
 ↓
Web / 印刷 / 電子書籍
```

SVGはピクセルの集合ではなく、線・面・文字・グループ・座標などを記述する。

つまり、

> SVG = 2次元の紙面を、編集可能な構造として記述するフォーマット

と考えられる。

## DTPXとの関係

DTPXを「意味としての原稿を、物理的な紙面へコンパイルする仕組み」と考えると、SVGはその紙面化を支える図形言語の一つになる。

```
文字列
  ↓
字形
  ↓
座標
  ↓
行
  ↓
段落
  ↓
ページ
  ↓
SVG / PDF
```

この考え方では、img2svgは単なる画像変換器ではなく、**ラスター画像からDTPXで扱える構造的な図形表現への入口**として位置づけられる。

## 役割

- raster image → SVG の変換実験
- DTPX向け図版生成
- SVGを中間表現として扱うための検証
- Web / 印刷 / 電子書籍への出力可能性の検討

## 関連

- DTPX: 編集された素材を紙面・出力へ変換する層
- EX / Editor X: 企画・編集・制作を統括する編集層
- make-book: 製本・印刷・流通まで含む出版層


## Python implementation

The first implementation is deliberately local-first:

```
raster
  ↓
JEV route (JSONL)
  ↓
VTracer
  ↓
SVG
  ↓
re-rasterize
  ↓
pixel diff / SVG structure report
```

VTracer is used as the deterministic raster→SVG engine; its official Python binding supports PNG/JPEG conversion and configurable tracing modes. citeturn0search0turn0search1

### Install

```sh
python -m pip install -e ".[verify]"
```

### Convert + verify

```sh
img2svg input.png -o build/input.svg --report data/runs.jsonl
```

The report contains the selected route and verification metrics.

### JEV routing

JEV can provide routing decisions as JSONL. The router accepts an `input`/`path` key and parameters such as `intent`, `engine`, `mode`, `hierarchical`, `max_colors`, and `filter_speckle`.

```sh
img2svg logo.png --jev data/jev.routes.jsonl --report data/runs.jsonl
```

This keeps the agent layer separate from the deterministic renderer: JEV decides **what kind of conversion to perform**, while VTracer performs the conversion.

Without a JEV decision, a small deterministic filename-based fallback selects sensible presets for logos, line art, photos, and generic graphics.

### Verification

SVG output is rendered back to the source image dimensions and compared with the original using Pillow. Installing the `verify` extra adds CairoSVG for SVG rasterization.

The verification result is intended as a DTPX pipeline signal, not as a claim that raster→vector conversion is lossless.

### Architecture

- `router.py` — JEV JSONL contract + deterministic fallback
- `vectorize.py` — VTracer adapter
- `verify.py` — SVG → raster → pixel-difference verification
- `report.py` — JSONL execution records
- `cli.py` — command-line pipeline
- `data/jev.routes.jsonl` — example JEV decisions