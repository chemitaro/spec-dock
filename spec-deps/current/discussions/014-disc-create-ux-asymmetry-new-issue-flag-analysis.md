# Discussion: `new issue --create-github-issue` 非対応による create UX 非対称の分析

## 問題

`initiative/epic` では GitHub create flag がある一方、`new issue --create-github-issue` は未対応で、issue だけ implicit default に依存している。

根拠:

- `manual-tests/reports/2026-03-15-manual-regression-sweep-github-live/summary.md`

## 現状分析

実際の挙動として issue は既定で GitHub create されるが、CLI 契約としては node kind ごとに surface が揃っていない。

## あるべき状態

- create command の引数 contract が一貫している
- implicit default があっても explicit flag で同じ意図を表現できる
- script/agent が node kind ごとの差を覚えなくてよい

## 対策案

### 案 A: `new issue --create-github-issue` を alias として追加する

利点:

- UX が一貫する
- 既存 default も壊さない

欠点:

- 引数は少し増える

### 案 B: 逆に initiative/epic 側の explicit flag を減らす

利点:

- surface を減らせる

欠点:

- 明示性が下がる
- 既存利用者への影響が読みにくい

### 案 C: help text だけで補う

利点:

- 実装が軽い

欠点:

- 非対称自体は残る

## 推奨案

`案 A` を採用する。

理由:

- additive change で後方互換を保てる
- agentic CLI では explicit intent を表せる方が扱いやすい

## consultant view

consultant も、`new issue --create-github-issue` を alias として追加するのが最も低リスクで、CLI 契約の非対称を解消しやすいと評価した。
