from gates.base_gate import BaseGate

# 3x4 gate grid: 3 depths x 4 gates per depth = 12 gates (dodecahedral face count)

# Depth 1: 4 NOR gates (outer -- Breath layer)
depth1_gates = [BaseGate(name=f"nor_d1_{i}", gate_type="NOR") for i in range(4)]

# Depth 2: 4 XOR gates (mid -- Blood/Word layer)
depth2_gates = [BaseGate(name=f"xor_d2_{i}", gate_type="XOR") for i in range(4)]

# Depth 3: 4 NOR gates (inner -- Sound/Flame layer, Bose-Einstein collapse point)
depth3_gates = [BaseGate(name=f"nor_d3_{i}", gate_type="NOR") for i in range(4)]

# Wiring: each depth-1 gate connects to 1 depth-2 gate,
# each depth-2 gate connects to 1 depth-3 gate,
# depth-3 gates connect back to depth-1 (toroidal fold)
for i in range(4):
    depth1_gates[i].connect(depth2_gates[i])
    depth2_gates[i].connect(depth3_gates[i])
    depth3_gates[i].connect(depth1_gates[i])  # toroidal fold

ALL_GATES = depth1_gates + depth2_gates + depth3_gates

GATES = {g.name: g for g in ALL_GATES}
