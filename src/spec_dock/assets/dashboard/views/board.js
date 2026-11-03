// 状態のボード。#531 がこのファイルを書き換えて作る（Epic R-13、R-14、D-08）。
import { emptySlot } from "./slot.js";

export default emptySlot({ id: "board", title: "ボード", icon: "table", owner: "#531", note: "止められている → 着手できる → 作業中 → マージ待ち の列" });
