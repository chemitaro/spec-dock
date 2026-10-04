# 第5回コードレビューの指摘分析

## 対象と証拠の境界

- 目的: Issue #413のP-03〜P-06およびP-07のGitHub Finish通常POSIX経路を、確定要件・設計・公開CLI契約と照合する。
- fixed point / merge-base: `6fec3099d8759b4e5b3b393b2987534b46dfa383`。
- レビュー対象: `4fc5bd259210501c17e8d24e4332746a6f46ea8e`。Strictのclean・upstream full SHA一致を確認して実行した。GPT-5.6 Sol / Proの通常browser経路で完了、wrapper exit 10、`review_status=fail`。
- 現行コミット: `a9e9997f427122db80e52bde27a1e65c7a1d2d31`。レビュー待機中にP-07の既存local Finishと、一回のselection観測からのtarget/handle固定を実装した。この後続コミットは今回のレビュー対象に含まれない。
- 後続の関連157 testsは通過済み。現在はP-08の未コミット変更もあるが、今回の指摘の証拠には用いない。P-08のfocused testsとenvelope既存testsは16件通過し、待機中の検証jobはない。
- 原文JSONは `code-review-p06-05.json` にbyte一致で保存した。レビュアーは静的照合であり、ローカルtest実行の証拠ではない。

`analyze-review-findings`を適用し、全3指摘、除外されたcoverage、既存の未完了義務を一括分析する。authorityはユーザーの確定判断、requirement/design、C-03/C-04、plan、AGENTS.md、実装/test evidenceの順に扱う。P0/P1は再レビュー通過までブロッカー。P2は単独で修正・再レビューを開始する条件にしない。ユーザーはIssue全実装、TDD、必要な修正・commit・Strict再レビューを許可しているが、設計意味の変更や本番cutoverはこの指摘から自動認可されない。

## F1: [P1] Finishが別snapshotのtokenを解除する

**妥当性・到達性**: 指摘はレビュー対象で成立する。`resolve_scope(@current)`内部のselection読取と、その後の`captured = read_selection`が別時点である。同一Scopeがclear→Startされた場合にも、遅いFinishが新tokenを捕捉して解除し得る。

**違反authorityと根本原因**: AC-413-15、D-08の「固定targetと捕捉handleをremote前に固定し、遅い解除が新tokenを消さない」。最初の誤りはapplicationの観測所有境界であり、Scope解決と解除handleを別観測にしていたこと。

**primary route**: `implementation-remediation`。提案を採用。現行`a9e9997`ではselectionを一回捕捉し、その同じ観測をtargetと`--expect-current`の両解決へ渡している。`test_finish_resolves_dynamic_target_and_handle_from_one_observation`は最初の観測終了直後の同Scope新tokenを保全し、旧token解除だけがunchangedになることを検証する。remote待機中のnative childによるclear→Start保全testも通過済み。

**保証・認可・帰結**: authority、public schema、永続化、lock、rollback保証は変更しない。既存のユーザー認可範囲内。追加の人間判断は不要。ローカル対処済みだが、後続SHAのfresh Strictで確認されるまでレビュー上のP1を合格とは扱わない。

## F2: [P1] Close未確認時のselection.clear段階がeffectsから消える

**妥当性・到達性**: 現行コードにも成立する。PATCHの成否不明または確認された失敗で`RemoteIssueError`となると、Closeのunknown/failedだけを追加し、保全した捕捉tokenの解除未実行を表示しない。既存のuncertain Close testもこの不完全なeffectsを期待していた。

**違反authorityと根本原因**: C-04の「実施しない段階はnot_attempted」、D-08およびremote-unknown exampleのClose未確認時の記録保全。最初の誤りはapplicationの段階別効果組立である。選択を保持する処理自体は成立するが、その未実行段階を外部へ伝えない。

**primary route**: `implementation-remediation`。解除対象handleを捕捉観測から一回決め、効果を組み立てる実行段階で停止した場合、未記録の`selection.clear`を`not_attempted`として補う。Close未知はcompleted=false/partial6、Close確認後・解除前の失敗はcompleted=trueと確認済みClose効果を維持する。初期GET等、操作を開始しない事前失敗は従来通りeffects=[]とする。

**検証計画**: 公開Finishの既存503 fixtureを先に修正して意図したRedを観測する。確認されたPATCH拒否、およびClose確認後・解除前の入力不整合も一つずつ公開CLIで検証する。既存local metadataの確認済み公開/確認不能な公開にも同じ未実行clear規則を適用し、Local Finish・selection・Gatewayの関連回帰を確認する。

**保証・認可・帰結**: 既存recordを自動消去/復活せず、retry・journal・Start lockは追加しない。public effect kind/statusの既存意味を満たす修正であり、設計の変更ではない。自律修正は既存認可範囲内。TDD/回帰/commit後にfresh Strictを行う。

## F3: [P2] 複数record解除の途中失敗で残りのeffectsが欠落する

**妥当性・到達性**: コードtraceでは成立する。複数の安全に捕捉できたrecordを明示`--all --yes`で解除する途中、`remove_observed`のconflictまたは通常OSErrorでは、現在failedと後続not_attemptedを積まずに外へ抜ける。既に成功した解除がある場合はpartial6を返すが、その後段の表示が欠落する。

**違反authority・root cause・route**: C-04の段階別effects精度。applicationのeffect組立が最初の誤りで、primary routeは`implementation-remediation`。P1と同じ一般的な表示不変条件を持つが、処理経路と複数handle境界は別である。

**parent policy・認可・帰結**: source-native P2を維持し、単独では再レビュー開始条件や新たな受入基準にしない。ユーザーは今回のIssue全実装を依頼し、「指摘事項があった場合には…レビューで指摘事項があった場合にはそのレビューの分析をし修正をして再レビュー」と指定している。この明示認可と既存P-07/C-04の正確なeffect出力を照合し、P1修正が既に必要な同じfail batch内で、複数handleの失敗/後続未実行の表示だけを最小限修正する。P2単独を理由に新campaignを開始する扱いではない。削除対象、承認、token保全、Start-only lock、schemaの意味を変更しないため、人間による設計判断は不要。

**検証計画**: 公開`active clear --all --yes`で3件の安全に捕捉可能なrecordを置き、2件目のOS unlink失敗を注入する。1件目succeeded、2件目failed、3件目not_attemptedとpartial6、後二recordのbytes保全を期待してRed→Greenを実施する。unlink後のfsync不明では当該unknown/後続not_attempted、捕捉済みrecordの変更では当該failed/後続not_attemptedを確認する。新tokenや未知entryを消す処理は追加しない。

## Coverageと残る義務

Windows immutable store/native受入、真正のlocal backend Finishの後続SHA、P-08以後、旧runtime退役、full lint/mypy/test、手動製品確認、Final Quality Gateは今回のレビューの製品完了認定対象外。これらを欠落指摘へ架空のseverityで変換せず、既存planの未完了義務として保持する。旧lifecycle CLI tests 4件はretired dispatcherに接続された証拠の更新が必要であり、通常runtimeへのfallbackを復活させない。

分析の帰結は、F2と明示認可範囲内のF3を既存意味を保ったTDDで修正し、F1の後続変更を含むcoherent unitを検証・commitしてfresh Strictを行うこと。今回のfailを破棄せず、現行SHAの合格までゲートを開かない。Goalはactiveのまま維持する。

## ローカル修正の検証

F2は既存503 testの必須clear not_attempted欠落をRedとして確認し、捕捉handleを一回決め、既にeffectを記録した実行段階で停止した場合だけ未実行clearを補った。初期GETやPATCH直前のmetadata前提失敗はeffects=[]を維持する。確認された422拒否、Close確認後・clear前のmetadata変更は追加の公開CLI検証で成立した。Finishの29 testsが通過した。

F3はOS unlinkの2件目で失敗するRed、最初のunlinkで失敗しeffectsが消えるRedを確認した。capture順を辞書順と仮定した初期fixtureは訂正し、実OS境界の第2呼出しで停止させた結果をRedの根拠にした。処理中のhandleだけfailed/unknown、後続captured handlesをnot_attemptedとして返す。適用済み/unknownがなければfailed5/3を保持し、false partialを作らない。directory fsync不明、先行unlink直後の外部record bytes変更によるconflictも追加Greenで保全を確認した。activeの36 testsが通過した。

これらはseverityを変更せず既存C-04の意味を満たす修正である。新しいlock、journal、state owner、Scope ID、rollback、未知entry削除、別WT操作は導入していない。全Ruff check/format（372 files）とactive/Finishの限定mypyが成功した。現在候補の独立再レビューは未取得のままであり、ローカルtestをStrict passの代用にしない。
