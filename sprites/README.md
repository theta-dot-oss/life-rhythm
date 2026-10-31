# ペンギンのスプライトシート

オリジナルの青いペンギン（丸い頭・座り姿・前向きの足の絵柄）で作ったアニメ用シートです。
1枚＝1本のアニメ＝1つの状態。コマは 320×320px、間隔 40px、背景は透明。アプリの
「キャラクターの画像」画面でそのまま選ぶと自動で切り分けられます。

| ファイル | 登録する状態 | 内容 |
|---|---|---|
| work-typing.png | 作業中 | ノートPCでタイピング |
| work-thinking.png | 作業中 | 考えごと→ひらめき |
| work-writing.png | 作業中 | 鉛筆でメモ |
| break-stretch.png | 休憩中 | 伸び＋あくび |
| break-tea.png | 休憩中 | お茶を飲む |
| break-music.png | 休憩中 | 音楽にあわせて首をふる |
| exercise-dumbbell.png | 運動中 | ダンベル |
| exercise-jump.png | 運動中 | ジャンプ |
| exercise-walk.png | 運動中 | 足踏み |
| rest-sleep.png | 休息・終了後 | 布団で zzz |
| rest-relax.png | 休息・終了後 | ソファでまったり |
| reward-cheer.png | ごほうび（終了直後） | 紙吹雪でばんざい |
| reward-love.png | ごほうび（終了直後） | ハート目 |
| reward-pump.png | ごほうび（終了直後） | 「だいちゃーじ！」ガッツポーズ |

`manifest.json` に同じ対応表が入っています。アプリはこのファイルを読み込んでシートを自動で取り込みます。
フィールド：`name`（ID、変更しない）、`name_ja`（登録画面に出す名前）、`file`、`state`（work/break/ex/sleep/happy）、
`frames`、`frame_size`、`gap`、`fps`（推奨コマ/秒）、`pingpong`（true なら往復再生）、`version`（絵を差し替えたら上げる）。

## 作り直し方

```
python3 tools/sprites/gen.py out && node tools/sprites/render.js out && python3 tools/sprites/assemble.py out
```

`gen.py` の `A[...]` に関数を足せばアニメを増やせます（Playwright の Chromium で描画）。

## 画像生成の絵からシートを作る

画像生成で作ったポーズ集（白背景、格子状に並んだ絵）は `tools/sprites/sheetify.py` でアプリ用シートにできます。
背景を透過にし、全ポーズを同じ縮尺にそろえ、足元を同じ高さに合わせて 320px のコマに並べます。

```
python3 tools/sprites/sheetify.py poses.png out --order 1,2,1,3,4,4 --name work-idea --state work --name-ja ひらめき --fps 2 --pingpong
```

`--order` はポーズ番号（左上から読み順、1始まり）の並び。省略すると全ポーズを順番に並べ、`out/frames/` に1コマずつも書き出します。
