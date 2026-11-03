# キャラクターのスプライトシート

アプリはページ読み込み時に `sprites/manifest.json` を読み、そこに並んだシートを自動で取り込みます。
いまは空（`[]`）です。シートはアプリの「キャラクターの画像」からアップロードして使っています。

## manifest.json の形式

```json
[
  {"name": "work-idea", "name_ja": "ひらめき", "file": "work-idea.png", "state": "work",
   "frames": 6, "frame_size": 320, "gap": 40, "seconds": 1.5, "pingpong": true, "version": 1}
]
```

- `name`：ID（変更しない）、`name_ja`：登録画面に出す名前、`file`：このフォルダ内のPNG
- `state`：work / break / ex / sleep / happy / due（呼びかけ中） / any
- `seconds`：1コマの秒数（1〜3推奨、初期値1.5）、`pingpong`：true なら往復再生、`version`：絵を差し替えたら上げる

## 画像生成の絵からシートを作る

白背景・格子状に並んだポーズ集は `tools/sprites/sheetify.py` でアプリ用シートにできます。
背景を透過にし、全ポーズを同じ縮尺にそろえ、足元を同じ高さに合わせて 320px のコマ（間隔 40px）に並べ、manifest 用のエントリも書き出します。

```
python3 tools/sprites/sheetify.py poses.png out --order 1,2,1,3,4,4 --name work-idea --state work --name-ja ひらめき --seconds 1.5 --pingpong
```

`--order` はポーズ番号（左上から読み順、1始まり）の並び。省略すると全ポーズを順番に並べ、`out/frames/` に1コマずつも書き出します。
