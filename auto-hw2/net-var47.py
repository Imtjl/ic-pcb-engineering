# import KiCad libs
import os

os.environ["KICAD8_SYMBOL_DIR"] = "/usr/share/kicad/symbols/"
os.environ["KICAD_SYMBOL_DIR"] = "/usr/share/kicad/symbols/"
os.environ["KICAD7_SYMBOL_DIR"] = "/usr/share/kicad/symbols/"
os.environ["KICAD6_SYMBOL_DIR"] = "/usr/share/kicad/symbols/"

# skidl lib for net creation
from skidl import *

print("🔧 Creating DIP-14 components...")
modules = [Part("Interface_LineDriver", "DS7820", ref=f"U{i}") for i in range(1, 20)]

print(f"✅ Created {len(modules)} modules")

print("🔌 Creating JST connector...")
connector = Part(
    "Connector_Generic",
    "Conn_01x12",
    ref="J1",
    footprint="Connector_JST:JST_XH_B12B-XH-A_1x12_P2.50mm_Vertical",
)

# parsed nets from picture
netlist_data = {
    1: [[3, 2], [5, 5], [4, 3], [19, 1], [12, 12]],
    2: [[18, 9], [17, 11], [16, 5], [15, 3], [19, 5]],
    3: [[19, 11], [19, 12], [4, 11], [3, 1]],
    4: [[12, 2], [8, 2], [5, 3], [11, 3]],
    5: [[16, 11], [8, 3]],
    6: [[12, 3], [14, 9], [3, 13], [17, 2], [6, 13]],
    7: [[19, 3], [17, 1], [19, 8], [19, 2], [17, 6]],
    8: [[5, 12], [19, 10], [16, 10], [11, 10]],
    9: [[15, 1], [10, 5], [19, 6], [3, 4], [14, 3]],
    10: [[10, 6], [12, 4], [19, 4], [11, 11], [11, 9]],
    11: [[18, 1], [14, 10], [12, 5], [5, 2], [17, 9]],
    12: [[19, 13], [4, 2], [6, 6], [16, 4]],
    13: [[19, 9], [7, 13], [14, 12], [11, 8], [18, 3]],
    14: [[11, 5], [3, 10], [10, 3], [1, 9]],
    15: [[18, 12], [13, 8], [4, 5], [1, 8]],
    16: [[14, 4], [15, 11], [2, 10], [14, 5], [18, 2]],
    17: [[5, 11], [1, 10], [17, 3], [18, 6], [17, 13]],
    18: [[12, 10], [16, 13]],
    19: [[18, 10], [8, 6], [15, 6], [18, 5], [14, 1]],
    20: [[8, 8], [8, 1], [3, 9], [3, 12], [12, 8]],
    21: [[12, 13], [13, 3]],
    22: [[11, 13], [14, 6], [12, 11], [8, 4], [9, 6]],
    23: [[1, 13], [14, 13], [13, 12], [5, 10], [18, 11]],
    24: [[17, 12], [12, 6], [14, 2], [8, 13]],
    25: [[17, 8], [1, 12], [16, 12], [11, 1]],
    26: [[16, 2], [16, 9], [6, 4], [17, 5], [18, 4]],
    27: [[11, 2], [1, 6], [1, 4], [15, 10], [6, 8]],
    28: [[2, 4], [15, 8], [14, 8], [3, 8], [2, 12]],
    29: [[7, 10], [10, 12], [14, 11], [3, 3], [5, 13]],
    30: [[16, 3], [15, 12], [5, 9]],
    31: [[5, 6], [18, 8], [2, 5]],
    32: [[18, 13], [1, 1], [15, 2], [1, 5], [4, 8]],
    33: [[1, 2], [5, 4], [3, 5], [11, 6], [15, 9]],
    34: [[16, 6], [5, 8], [12, 1]],
    35: [[15, 13], [2, 8], [13, 1], [2, 11], [16, 8]],
    36: [[1, 11], [8, 5], [15, 5], [17, 10], [11, 12]],
    37: [[8, 10], [17, 4], [4, 4], [8, 11], [5, 1]],
    38: [[16, 1], [12, 9], [9, 2], [9, 5]],
    39: [[15, 4], [6, 12], [11, 4], [7, 2], [9, 10]],
    40: [[9, 12], [10, 9], [2, 9], [2, 13], [4, 1]],
}

# nets that go to jst connector
jst_connections = [30, 10, 23, 21, 35, 26, 2, 13, 17, 40]

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

print(f"\n🔌 Connecting nets to JST connector...")

for i, net in enumerate(jst_connections):
    if net in nets:
        nets[net] += connector[i + 1]
        print(f"✅ net{net_num} → JST pin {i+1}")

print(f"\n💾 Generating netlist...")
generate_netlist(file_="complete.net")

print(f"\n🎉 Done!")
print(f"📊 Stats:")
print(f"  Modules: {len(modules)}")
print(f"  Nets: {len(nets)}")
print(f"  JST connections: {len(jst_connections)}")
print(f"  File: complete.net")

print(f"\n💡 Import complete.net into KiCad pcb editor:")
print(f"  Tools → Update PCB from Schematic → Import Netlist")
