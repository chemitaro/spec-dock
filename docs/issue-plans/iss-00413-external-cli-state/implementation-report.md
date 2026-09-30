# Issue #413 実装記録

## 作業契約

2026-09-30の利用者指示に基づき、レビュー合格済み要件・設計・計画に沿ってTDDで段階実装する。区切りごとに検証・コミット・GPT-5.6 Sol / ProによるChatGPT Code Review Strictを行い、必要な指摘の分析・修正・再レビューを実施する。最終候補ではStrict Final Quality Gateと独立した必須試験、実consoleによる手動動作確認を完了する。

必要な具体化にはImplementation Brief Strictを利用する。実装担当の契約はGPT-6.1 Sol / High。人間によるPRマージ、package公開、実環境適用は製品実装・検証と別の証拠として扱う。

- 製品基準: `6fec3099d8759b4e5b3b393b2987534b46dfa383`
- 独立仕様レビュー合格対象: `7e895803cba0d43957e504c9f97637d307bc6a78`
- 実装開始HEAD: `f0280a9e80ab50f960e8298ce11a2c7c7cc821f4`
- branch: `codex/iss-00413-external-cli-state`
- 正本: [要件](requirement.md)、[設計](design.md)、[計画](plan.md)、[CLI契約](artifacts/cli-contract.md)

## P-01 基準取得と最初のRed

変更前の通常試験を実行した。

| コマンド | 実結果 |
|---|---|
| `make lint` | exit 0。ruff check、format check、mypyすべて成功 |
| `uv run pytest` | exit 0。1217 passed、1 skipped、274.82秒 |
| catalogとC-01の照合 | 44 leafが各一回だけ対応。追加・欠落0 |

`tests/cli_runtime/test_issue413_contract.py`の最初の公開入口テストでは、GitHub-backed schema3の独立したconsumer fixtureを作り、controlなしのScope読取を要求した。`main(... scope show init-00001 --json)`は、固定配布レイアウト検証の`ENGINE_PREFLIGHT_FAILED`でexit 3になり、期待するexit 0との差を実際のassertionで検出した。collection/import障害ではない。P-02の通常package入口とP-04のcontrol不要contextでGreenにする対象である。

240件の実Scope metadata、workspace宣言、確定インタビューの変更前hashをWorkBenchに保存した。実Scopeの手編集・旧engineの起動・正式Startの代替操作は行っていない。

P-01は進行中。Git原文・親昇格・Start以外の共通排他の回帰は、それぞれの公開経路を実装する段階で一つずつRed→Greenを確認し、本記録へ追記する。

## P-02 通常packageとutilityの縦経路

138 Python moduleをasset配下から`src/spec_dock/runtime/`へ移し、source/testのimportを`spec_dock.runtime`へ統一した。旧asset directoryをsys.pathへ追加するtest導線を除去した。通常consoleは静的parser/presentationだけを読み、help/version/completionをv2 JSONで返す。業務は現時点で非0の`BUSINESS_NOT_CONNECTED`となり、旧fixed engineへfallbackしない。

installed metadataをversion正本とした。static資産は`importlib.resources.files`から取得する。dogfoodの旧runtimeは実切替前の資料として保持し、provider/static資産の比較からその退役対象だけを分離した。

| 検証 | 実結果 |
|---|---|
| fresh wheel →別venvの非editable install →実console | 成功。Git/ghなし、壊れたproject、root/44leaf help/version/3補完、v2 JSON |
| installed processのimport観測 | utilityでapplication/commands/infra/domain.operation/fixed_bundle/runtime_loaderのimportなし |
| 独自version.txtを9.9.9へ変更 | versionはpackage metadataの0.2.4を維持 |
| sdistから再buildしたwheel | 通常runtime138 moduleとhidden/static資産の収録集合が直接wheelと一致 |
| utility/catalog/TTY lifecycleの関連試験 | 48 passed |
| unit全体＋utility/catalog（static parity修正前） | 764 passed、1 skipped、旧runtime複製parityの1件失敗 |
| static parity修正＋validate/deps関連 | 37 passed |
| 旧fixed-entrypointのcharacterization | 14 passed、旧fixed engineによる2consumer initの1件失敗。新installationはP-12で置換する |
| Ruff check/format | 成功 |
| mypy | 未合格。正常subpackage化で旧namespaceのmissing-import/Anyが解消し、潜在的な型不整合が顕在化。共通fixtureをTypedDictに修正後も737件が残る。隠蔽・gate緩和はしない。退役module/testは担当stepで除去し、残存型はP-13の必須gateまでに修正する |

Implementation Brief Strictは実装開始SHA `f0280a9e80ab50f960e8298ce11a2c7c7cc821f4`に固定し、GPT-5.6 Sol / Proで完了した。[相談記録](https://chatgpt.com/g/g-p-69fd45693ed48191a7defd8273c37115-for-codex-app/c/6abcafd4-1f58-83e8-9592-c163a0a18244)。回答を正本と照合し、utilityとbusinessのimport分離を追加した。ブリーフの助言を製品試験成功とは扱わない。

2026-09-30の利用者指示で一時的にChatGPT Manual Useを選択したが、新規送信前にOracle復旧の指示で解除された。以降のレビューは通常Strict wrapperを使う。

## 現在の段階

P-02のutility/packageは検証できたが、全gateは未合格。P-03〜P-17は未着手。これは途中checkpointであり、全機能の受け入れ、コードレビュー、最終品質ゲート、手動動作確認は未実施。受入AC-413-02のbusinessまで含む成功を主張しない。
