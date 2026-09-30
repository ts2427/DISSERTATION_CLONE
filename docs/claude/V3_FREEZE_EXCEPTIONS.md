# v3 freeze exceptions — Run-All Follow-Up Stage 2 (2026-09-29)

**The manifest is NOT modified.** `outputs/rebuild_v4/V3_FREEZE_MANIFEST.csv` still
records the pre-Stage-2 bytes of every file below, and `210 --create` was not run. This
file is a narrow, pinned override read by `scripts/210`: it admits **exactly these 13
paths at exactly these new hashes, and nothing else**.

What that buys, and what it deliberately does not:

- A **further** change to any of these 13 files fails the gate. The new hash is pinned,
  not the path, so the exception is spent the moment the file moves again.
- A change to **any other** baseline file fails the gate, exactly as before.
- The old hash is pinned too, so the exception cannot be reused against a different
  starting state - if the manifest is ever rewritten, every exception here stops matching
  and the gate fails closed.

**The full re-freeze - a new manifest and a new tag - happens only at the rebaseline.**
Until then the gate reports these as authorised exceptions, listed individually, so the
fact that 13 baseline files moved is never hidden by a PASS.

## Why v3 files were touched at all

Six of the thirteen are v3-chain scripts (155, 156, 158, 163, 165, 199), and the prime
directive is *v3 does not change*. Each edit was individually ruled by Tim on 2026-09-29:
G1 and G2 removed an Essay 3 result and a significance verdict on a disqualified rung from
`scripts/158`; I2 added sample-size tripwires to the steps that build a sample; J2 moved
retired strings out of live log text. **No edit changes an estimate, a sample, or a
verdict.** G1 removes keys; G2 renames a label; I2 adds assertions that pass; J2 rewrites
comment and log strings. `scripts/195` and `scripts/220`, the frozen classifiers, were
NOT touched - see the note at the end.

## The 13 files

`scripts/210` parses the table below. Each row is
`| path | old sha256 | new sha256 | old blob | new blob | commits | parts |`.

| path | old sha256 | new sha256 | old blob | new blob | commits | parts |
|---|---|---|---|---|---|---|
| `outputs/RETIREMENT_LEDGER.md` | `72cf6c3f36e65d8b9a86ca06a507d1d0d2ed17b55842ee8db186aec2700d38f2` | `89ea491253dde4bee055080394e77384d99d201eeb40720f3c040a29abd99a38` | `09b80559527d23c4af24e3a51ce13d989f4d4772` | `5ee4e2602c90254845aed8df6b9d75c76f61555d` | 881123b 69027d5 7cea236 7914d97 f5c6bca 438814f bf57474 9ab0ce4 | F1 G1 G2 H J1 J2 J3 L |
| `run_all.py` | `ee43a71ed528acc0d0705aa69d4651e989eead0742fd8fdf74ed2e868d16aba9` | `9ad925c0bd80e3c90b0af667b3025f3755e1b8dffbb4dbd56d313b9e2b941ed2` | `ab88ffcfe5f12b640b889350732468e02a6b5455` | `f167d2fe9183f50074386fe01e74c16f217143a3` | 881123b 7914d97 f5c6bca bf57474 dc5607f a91c5be e048b97 | F1 H J1 J3 I1 K |
| `scripts/155_rebuild_s5_outcomes.py` | `0f441cdea26a8e7fc9f4d0bc670c7e5fe6a0d506d2f75736172a25fe90f965a7` | `faa3ebc0594e223ec0359cf1ab0ac62b5319ed27daa38ba9ab462901aad44c50` | `361500eb10c0c487657ef4979698c957a4f0e6bf` | `edb7f02bb694f71cd650030e754468f1785ba6c6` | fd1a563 | I2 |
| `scripts/156_rebuild_s6_assembly.py` | `01908269ec892a961a21c1eb0761d04dee0739cd87406eb802c8ac60e1784d9d` | `db59fd5da9ac5c06867d6f3b74b83b65febd718eb2770556612458dfe026bd93` | `58dff508865982540f7c467c843228bd3e8a1dbe` | `f7ef0efa39bc83778b8da697aa51f1066da891e5` | fd1a563 | I2 |
| `scripts/158_rebuild_s8_regenerate.py` | `c5b31801401d725b40e5a0cb1fe9ae2c49ddcfa214d185bb74bf6d10f8901ef9` | `38887009cc9d7fa4fefa63cf1a8c5075fbf5261e4bb88c144111bd5e9b2db2a3` | `255c4fa963aec2ef9c49eeebe969fcf2d7bae0e1` | `afade151558d57154d1c146386d6cedf6b2c825e` | 69027d5 7cea236 | G1 G2 |
| `scripts/163_essay2_rerun_form499.py` | `399fe1f993f3cf8a1ce1dcf49121a6907185b9c136379c6ae2c45bda241d717a` | `d926ecefddf6a724d21dc883ab45ede9232f078e47c137f7b2299a6864d79f93` | `7045661586e1bd10bd47977f9b442efe69b51398` | `9c45e323356347a45c3ab7e3898f1a586c9e35c5` | 438814f fd1a563 | J2 I2 |
| `scripts/165_essay2_inference_ladder.py` | `9a67c8b1ad00524c9cc15c6130aa2421c65b33143a8544ece622aad5b3a2f073` | `13f73ae2a959aba49f7b2f120ca17aecb2492f899683a0ae2e43ec2312d40253` | `f65747c86e7d5f79e0850a9e13e3f9ac93789934` | `9765de43b9f26ac06d132604bfa38a003a7ed355` | fd1a563 | I2 |
| `scripts/199_essay3_q2_sample_e.py` | `0f01da3c3e1b53bac201eb039af85df9993976519ccc35a0f7034dd90241f082` | `a26819f538b66f0de1dac2f00f9b538e160686b34295af71f5953e7c6f1441e9` | `99a877bce5db379941ca3c1ed9dfddcf7199eb48` | `3f1b7b24233d418b3c6e6c7338e62fd3cf250514` | fd1a563 | I2 |
| `scripts/robustness_1_alternative_windows.py` | `cbaddadf3d9d56f66b4d864b13f081e06f94241acc16f9d28fd5964588f8359e` | `576ea4d9c997682c025756c510e8873eaee1d34df680075f35afe5ad9c51bfd7` | `add3f05d5ff9241ac4e0678ab03f67d3c39832c3` | `6d78dd9fd4973f2bf02cab4e26eecd9db58c821f` | 438814f | J2 |
| `scripts/robustness_2_timing_thresholds.py` | `f848eac7e103b7072dcbfab62e914a761febea65971724465681e682b46adf90` | `54d80c419620fb02458f1ed55e16a4cd5062f6f80e0486ec08ae68682a37d098` | `8c921713294f6ad4871dfa65a84cf28042a9af4b` | `8966bb07616d266b16e30592211a894a52ef95b3` | 438814f | J2 |
| `scripts/robustness_3_sample_restrictions.py` | `e2fb1c387f0c1e21e25398e2f1be29d21e7fa10e1fc19639088566b619cb704b` | `2232f2e776dcf4ca680535316e7f7baf89ee609c9ed01a280dfc7bba9bc996e4` | `3c28aac47859308fa6a79f14bdf9a1947f0f0923` | `7bad5532800ccd38e3e1c7faceb5d5e3bf1b91d7` | 438814f | J2 |
| `scripts/robustness_4_standard_errors.py` | `71e550f46dbbbac60a89655d244ad8b744432991bc4354a13f3da1a01362a740` | `5737ed94a39e04481fd473753f1188c4b4398222f6730474abebc5e932b6339a` | `6378558d1761a9a083cc98f04638b4235ee45ff5` | `b097d136ea10a76e76dfcedb3cafc6f7195dfd22` | 438814f | J2 |
| `scripts/robustness_5_fixed_effects.py` | `3f4524192d7bffedaa95d32ea9bb3e8dc07a3e1f49b23df3e597d0b22be64f72` | `3712623092888b999553ea1c9dfe9ecfca18dd4623c882e450c390eb6df2dcc0` | `0e206a095baf40adf0bb0bfb18b0182c4cbdd0c2` | `f7f8f8c484fd9f641781a678d46eac942f4d99fd` | 438814f | J2 |

## What each change was

**`outputs/RETIREMENT_LEDGER.md`** — F1 (the v4 chain staged as authoritative, Query 2 relabelled RETIRED); G1 (the 13 Essay 3 H6 keys removed); G2 (the HC3 status label may no longer read SIGNIFICANT); H (28 steps retired); J1 (duplicate step declaration removed); J2 (retired strings moved out of live script text); J3 (six dead commented-out tuples deleted); L (the essay2_appendix tombstone recorded)

**`run_all.py`** — F1 (the v4 chain staged as authoritative, Query 2 relabelled RETIRED); H (28 steps retired); J1 (duplicate step declaration removed); J3 (six dead commented-out tuples deleted); I1 (the executable LFS guard); K (scripts/247 staged after 160)

**`scripts/155_rebuild_s5_outcomes.py`** — I2 (sample-size tripwires)

**`scripts/156_rebuild_s6_assembly.py`** — I2 (sample-size tripwires)

**`scripts/158_rebuild_s8_regenerate.py`** — G1 (the 13 Essay 3 H6 keys removed); G2 (the HC3 status label may no longer read SIGNIFICANT)

**`scripts/163_essay2_rerun_form499.py`** — J2 (retired strings moved out of live script text); I2 (sample-size tripwires)

**`scripts/165_essay2_inference_ladder.py`** — I2 (sample-size tripwires)

**`scripts/199_essay3_q2_sample_e.py`** — I2 (sample-size tripwires)

**`scripts/robustness_1_alternative_windows.py`** — J2 (retired strings moved out of live script text)

**`scripts/robustness_2_timing_thresholds.py`** — J2 (retired strings moved out of live script text)

**`scripts/robustness_3_sample_restrictions.py`** — J2 (retired strings moved out of live script text)

**`scripts/robustness_4_standard_errors.py`** — J2 (retired strings moved out of live script text)

**`scripts/robustness_5_fixed_effects.py`** — J2 (retired strings moved out of live script text)

## Not touched

- **`scripts/195_essay3_q2_classifier_v2.py`** — the frozen Query 2 classifier (commit
  `6f7be7a`, blob `ec32364`). Part I2 named it, but its identity is recorded in
  `ESSAY3_HANDOFF.md` and `ESSAY3_POST_RERUN_STATE.md` and its EOL is pinned in
  `.gitattributes` so its logged sha reproduces; any edit would invalidate the blind
  validation and require a fresh round. Its assertion went to `scripts/199` instead.
- **`scripts/220_essay3_v4_classifier_v2.py`** — the v4 classifier, frozen and
  byte-identical in method to 195.
- **`scripts/150`-`154`, `157`** — the v3 chain steps no ruling reached.
- **`docs/claude/ESSAY3_POST_RERUN_STATE.md`** — Tim's document. It still describes the
  Query 2 build as current; superseded by pointer, never by edit.
