# Issue 370 candidate-wide Full Regression evidence

This directory is an immutable copy of the verifier output for the implementation
candidate `d13d65fc76a30f212e88e925026fd35b3448e8ac`.

- command: `uv run python .../iss-00368-recognized-workspace-reconciliation/artifacts/verify-full-regression.py --timeout-seconds 1200 --max-total-seconds 1800 --shards 4`
- collected nodes: 2507 (the complete inventory is `collection.log`)
- result: `verified`
- approved failure signatures: 27 (exact match)
- missing failures: 0
- signature mismatches: 0
- unexpected failures/errors: 0
- collection: 0.329 seconds
- shard elapsed: 624.714 seconds
- total elapsed: 625.085 seconds
- hard SLO: 1800 seconds (`pass`)
- advisory target: 600 seconds; this is not a release-blocking bound

`result.json` contains the verifier's exact candidate SHA and shard references.
The four `shard-*.xml` files are the raw JUnit results, the four `shard-*.log`
files are the raw pytest logs, and `collection.log` is the raw collection
inventory. The first verifier attempt for this SHA was discarded because an
untracked evidence directory made the repository receipt test fail; the
verified rerun recorded here was executed from a clean worktree.

SHA-256 manifest:

| file | SHA-256 |
|---|---|
| `README.md` | generated with this evidence publication |
| `collection.log` | `3ba5180b265ea7188187a4341aea3ebb4d8984240e5f1b8363d78d4c54a14a45` |
| `result.json` | `c544d125a097cb57fee28b61540fe1e8b3855372c6ac772a49292f412120d1d9` |
| `shard-1.log` | `4f2b60f2665b94baabe84673c1543ca968fa3916bebfe1efa3398c10c3803968` |
| `shard-1.xml` | `3059313d7b2aa85d5f9761eb897f48b7cfecaf1a4f59bacf07506ee8c40d73e0` |
| `shard-2.log` | `cb174103f35c8cbc5e65a81bf828c6074e740e17151b160695250253b9bf9ff3` |
| `shard-2.xml` | `327b6e22855ac7bfc97fb1327775a5ff992bebea3d7e32904ca15a6160e20bb8` |
| `shard-3.log` | `b58f6d1695e82142fed79dcf7a37fb9c6abaad21f83037e6b1497a71e45f7156` |
| `shard-3.xml` | `c361818fc69c5f6d98836374b48858a7e05266904ba77fd542d5a819cf701c2e` |
| `shard-4.log` | `993795d802217083090a8e803972dcfa3e0c95883fc6f0ac75551919b79cdd5a` |
| `shard-4.xml` | `4352ecb0efd664b66b4c1cae525b6d08d2a55053f1265e8a4a9e99f0063f35e2` |
