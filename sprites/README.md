# ペンギンのスプライトシート

オリジナルの青いペンギン（アプリの SVG ペンギンと同じデザイン）で作ったアニメ用シートです。
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

`manifest.json` に同じ対応表（state: work/break/ex/sleep/happy）が入っています。

## 作り直し方

```
python3 tools/sprites/gen.py out && node tools/sprites/render.js out && python3 tools/sprites/assemble.py out
```

`gen.py` の `A[...]` に関数を足せばアニメを増やせます（Playwright の Chromium で描画）。
