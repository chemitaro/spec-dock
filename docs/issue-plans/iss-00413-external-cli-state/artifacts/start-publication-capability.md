# Startで既知の未対応公開原語をGit変更前に拒否する

2026-10-02、baseline 578f27e3c125fd6cfd0c448ec06ee0e716f6337c（clean）。D-03の無上書き公開とD-05/D-06の副作用前停止に沿う追加修正です。Scope公開の事前判定をStartにも接続し、Windows保存対応を完成扱いにはしません。

## 再現と変更

必要なnative rename symbolが存在しない外部OS/library境界を供給すると、公開work startは新branchを作成してcheckoutを済ませ、stageを残した後で停止しました。結果はpartial/exit6、branchとcheckoutはsucceeded、selection.publishはunknownでした。これは使い捨て実Git fixtureでの再現であり、本consumerやlive GitHubへの変更ではありません。

公開CLIから期待exit5に対しexit6となるRedを1 failed（0.66秒）で観測しました。Startのメモリ上の計画が新規公開または記録置換を必要とする場合、既存のrequire_directory_publication_supportを、dry-run成功判定・Start lock・Git変更より前に呼びます。probeのfile作成はなく、GitHubへのGETは従来のreadiness観測だけです。

同じ一件のGreenは1 passed（0.27秒）。次に三階層・apply/dry-run・未対応platform/欠落symbolの12組、捕捉した既存記録の置換拒否2組、公開を伴わない同一対象Startの維持2組を確認し、16 passed/84 deselected（3.93秒）、exit0となりました。最初のGreen出力はツール出力に保持し、最終green logには16組の結果を保存しています。

既知の未対応ではstatus=failed/exit5、started=false、effects=[]です。branch/HEAD/ref、捕捉した旧記録、tracked本文/metadataとfixtureの全bytesが変わらず、新stageも独自.git領域も作りません。同じ妥当な直接対象・同じbranch/HEADに対する公開不要のStartは従来どおりunchangedで、既存tokenを保ちます。

この確認はOS/libraryの既知の能力だけです。kernel・filesystemの実操作、同期、後からの権限/identity変更まで保証しません。原語は存在するが実際のrenameが失敗する場合や、公開後の同期が失敗する場合は、既存どおり実際のGit効果・残存stageとpartial/unknownを報告し、自動rollbackしません。

## 実際に行った検証

| 確認 | 実際の結果 |
|---|---|
| macOS arm64・実Python3.12.11 / 関連8 suite | 266 passed、102.42秒、exit0 |
| macOS arm64・実Python3.10.15 / 同8 suite | 266 passed、102.77秒、exit0。prefix/version/provider import元を実行guardで照合 |
| 通常make lint | Ruff check/format300 file、mypy219 source file、exit0 |

関連8 suiteは公開Start/active/Finish、実Git Start integration、純粋Start plan、work-target store、Scope公開、fresh wheel実console E2Eです。実console E2Eも通常pytestの一部であり、今回の手動操作結果と称しません。GitHubはfake APIまたは外部stateful fake ghを使い、実Windows/NTFS成功には読み替えません。

元logはEpicのignored Workbench、iss-00413-implementation/pytest-start-publication-capability-{red,green,related,python310}.logとlint-start-publication-capability.logです。Source/testのsha256は次の通りです。

    work_start.py: a2cb777b07888d2cd5934a949acb6d26043944f099b47260bb3c06a5b385ad6d
    test_issue413_work_start.py: cde8430ec2ef87b6a7269f45b0172db3425254048de692f0b63ac21d0faf126c
    json_store.py（今回変更なし）: ba9850a8d31176d8c5b894d77aed6d93f696fb7f8175ccfb96f19fd3f0e2ae5b

## 残る条件

[全件1900件と手動14操作](macos-full-75ac5760.md)は75ac5760の製品sourceの証拠であり、今回のStart追加変更を含みません。現在候補の全件・最終手動確認、[Windows保存/native受入](windows-adapter-connection-review.md)、fresh Code Review StrictとFinal Quality Gateは引き続き必要です。P-03/P-06/P-13の完了認定、実consumer切替、正式#413 import/Startをこの一単位で完了にはしません。
