# import KiCad libs
import os

os.environ["KICAD8_SYMBOL_DIR"] = "/usr/share/kicad/symbols/"
os.environ["KICAD_SYMBOL_DIR"] = "/usr/share/kicad/symbols/"
os.environ["KICAD7_SYMBOL_DIR"] = "/usr/share/kicad/symbols/"
os.environ["KICAD6_SYMBOL_DIR"] = "/usr/share/kicad/symbols/"

# skidl lib for net creation
from skidl import *

print("🔧 Creating DIP-14 components...")
modules = [Part("Interface_LineDriver", "DS8830", ref=f"U{i}") for i in range(1, 20)]

print(f"✅ Created {len(modules)} modules")

print("🔌 Creating PinSocket connector...")
connector = Part(
    "Connector_Generic",
    "Conn_01x12",
    ref="P1",
    footprint="Connector_PinSocket_2.54mm:PinSocket_1x12_P2.54mm_Vertical",
)

netlist_data = {
    1: [[12, 6], [1, 11], [14, 13], [14, 4]],
    2: [[11, 1], [7, 3], [7, 5]],
    3: [[11, 5], [10, 12], [18, 6], [13, 2], [19, 2]],
    4: [[16, 8], [4, 10], [7, 11], [12, 3], [18, 10]],
    5: [[4, 13], [7, 9], [11, 6], [12, 2], [10, 13]],
    6: [[4, 11], [4, 3], [15, 9], [2, 4]],
    7: [[16, 11], [10, 11], [13, 3], [1, 12]],
    8: [[19, 11], [5, 11]],
    9: [[4, 12], [3, 9], [14, 6]],
    10: [[1, 5], [2, 8]],
    11: [[10, 3], [11, 3], [1, 10], [13, 11], [17, 13]],
    12: [[19, 9], [4, 2], [18, 13], [3, 13], [9, 1]],
    13: [[14, 10], [15, 11], [19, 12]],
    14: [[19, 10], [8, 13]],
    15: [[2, 11], [1, 1], [7, 4]],
    16: [[19, 8], [19, 6], [15, 5], [13, 1], [7, 8]],
    17: [[11, 8], [10, 10], [13, 6], [5, 6]],
    18: [[7, 6], [19, 3]],
    19: [[6, 8], [16, 12], [7, 2], [18, 5], [18, 4]],
    20: [[16, 4], [4, 4], [13, 12], [3, 8], [2, 12]],
    21: [[18, 2], [3, 4], [19, 4]],
    22: [[17, 4], [19, 13], [14, 2], [19, 1]],
    23: [[15, 4], [10, 8], [15, 12], [2, 5], [19, 5]],
    24: [[6, 13], [6, 11]],
    25: [[13, 8], [12, 5], [16, 6]],
    26: [[5, 9], [16, 10], [15, 3], [1, 13], [7, 1]],
    27: [[15, 13], [15, 8]],
    28: [[3, 11], [2, 2], [2, 3]],
    29: [[18, 1], [18, 12], [13, 5], [15, 6], [15, 2]],
    30: [[4, 6], [6, 3], [18, 11], [11, 11]],
    31: [[18, 3], [13, 4], [11, 9], [17, 3]],
    32: [[6, 9], [9, 5]],
    33: [[14, 9], [2, 9], [6, 2], [13, 10], [13, 9]],
    34: [[18, 9], [11, 4], [12, 11], [18, 8], [9, 4]],
    35: [[6, 12], [13, 13]],
    36: [[3, 2], [2, 6], [4, 1], [9, 13], [16, 3]],
    37: [[11, 13], [1, 8], [16, 13], [7, 12], [7, 13]],
    38: [[10, 9], [3, 12], [17, 11], [3, 5], [17, 8]],
    39: [[11, 10], [16, 5], [15, 10]],
    40: [[9, 8], [12, 13], [17, 6], [11, 2]]
}

jst_connections = [28, 5, 40, 38, 7, 30, 32, 18, 21, 29]

print("⚡ Creating power nets...")

# create gnd and vcc nets
vcc = Net("VCC")
gnd = Net("GND")

for mod in modules:
    vcc += mod[14]
    gnd += mod[7]

vcc += connector[11]
gnd += connector[12]

print(f"🕸️ Creating all {len(netlist_data)} connection nets...")

nets = {}
for net_num, connections in netlist_data.items():
    net = Net(f"net{net_num}")

    for mod, pin in connections:
        if mod <= len(modules):
            net += modules[mod - 1][pin]
        else:
            print(
                f"we only have {len(modules)} modules (error: {mod} module doesn't exist)"
            )

    nets[net_num] = net
    print(f"✅ net{net_num}: {len(net.pins)} connections")

print(f"\n🔌 Connecting nets to PinSocket connector...")

for i, net in enumerate(jst_connections):
    if net in nets:
        nets[net] += connector[i + 1]
        print(f"✅ net{net_num} → PinSocket pin {i+1}")

print(f"\n💾 Generating netlist...")
generate_netlist(file_="complete.net")

print(f"\n🎉 Done!")
print(f"📊 Stats:")
print(f"  Modules: {len(modules)}")
print(f"  Nets: {len(nets)}")
print(f"  PinSocket connections: {len(jst_connections)}")
print(f"  File: complete.net")

print(f"\n💡 Import complete.net into KiCad pcb editor:")
print(f"  Tools → Update PCB from Schematic → Import Netlist")
