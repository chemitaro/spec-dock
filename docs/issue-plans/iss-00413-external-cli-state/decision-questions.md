# 旧質問票の置換 — 確定回答と技術設計へ

以前の質問票と完全stateless草案は採用しません。2026-09-30の [利用者確認済みinterviewのコピー](artifacts/user-decisions.md) が新しい要求の証拠です。Codexが保持する [ローカル原記録](artifacts/interview-worktree-start.md) は本ZIPで生成・上書きしません。

同じcloneだけ、Startはbranch作成/checkoutを含む、一worktree一直接対象、Finishは完了/Close、三階層維持、Release追加なし、Finish後branch保持、失敗時は巻戻しなし/Git原文表示が確定しています。これらを再質問したり、旧草案を根拠に逆転したりしません。

[設計D-01](design.md#d-01) は保存path・OS原語・activeの最小制限などを**技術的選択**として示します。利用者が各実装細部を逐語承認したとは記録しません。[要件の実装開始条件](requirement.md#start-conditions) を確認し、実装で重大な矛盾が見つかった場合だけ該当箇所を停止してください。
