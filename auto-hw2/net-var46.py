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

print("🔌 Creating JST connector...")
connector = Part(
    "Connector_Generic",
    "Conn_01x12",
    ref="J1",
    footprint="Connector_JST:JST_EH_S12B-EH_1x12_P2.50mm_Horizontal",
)

# parsed nets from picture
netlist_data = {
    # Цепь #1: 7/12, 18/12, 15/3
    1: [[7, 12], [18, 12], [15, 3]],
    
    # Цепь #2: 13/5, 11/13, 3/1, 13/2, 16/11
    2: [[13, 5], [11, 13], [3, 1], [13, 2], [16, 11]],
    
    # Цепь #3: 6/11, 1/10, 18/13
    3: [[6, 11], [1, 10], [18, 13]],
    
    # Цепь #4: 15/2, 17/4
    4: [[15, 2], [17, 4]],
    
    # Цепь #5: 10/3, 6/2
    5: [[10, 3], [6, 2]],
    
    # Цепь #6: 6/5, 9/9, 15/11, 18/8, 1/11
    6: [[6, 5], [9, 9], [15, 11], [18, 8], [1, 11]],
    
    # Цепь #7: 18/10, 16/2, 17/1, 17/12
    7: [[18, 10], [16, 2], [17, 1], [17, 12]],
    
    # Цепь #8: 15/13, 7/6
    8: [[15, 13], [7, 6]],
    
    # Цепь #9: 16/13, 17/3, 12/13, 8/4, 7/5
    9: [[16, 13], [17, 3], [12, 13], [8, 4], [7, 5]],
    
    # Цепь #10: 3/9, 15/4, 16/3, 18/11
    10: [[3, 9], [15, 4], [16, 3], [18, 11]],
    
    # Цепь #11: 4/2, 9/11
    11: [[4, 2], [9, 11]],
    
    # Цепь #12: 18/3, 14/1
    12: [[18, 3], [14, 1]],
    
    # Цепь #13: 7/10, 17/5, 18/4, 18/9
    13: [[7, 10], [17, 5], [18, 4], [18, 9]],
    
    # Цепь #14: 17/6, 2/6, 18/5, 10/5, 3/6
    14: [[17, 6], [2, 6], [18, 5], [10, 5], [3, 6]],
    
    # Цепь #15: 14/5, 12/12, 16/8, 18/1, 18/6
    15: [[14, 5], [12, 12], [16, 8], [18, 1], [18, 6]],
    
    # Цепь #16: 16/9, 18/2, 16/6, 9/12, 13/10
    16: [[16, 9], [18, 2], [16, 6], [9, 12], [13, 10]],
    
    # Цепь #17: 17/13, 14/6, 9/13, 7/3, 16/10
    17: [[17, 13], [14, 6], [9, 13], [7, 3], [16, 10]],
    
    # Цепь #18: 16/1, 16/12, 3/11, 10/12, 10/8
    18: [[16, 1], [16, 12], [3, 11], [10, 12], [10, 8]],
    
    # Цепь #19: 14/3, 17/8, 16/5, 2/8
    19: [[14, 3], [17, 8], [16, 5], [2, 8]],
    
    # Цепь #20: 16/4, 12/3
    20: [[16, 4], [12, 3]],
    
    # Цепь #21: 14/11, 13/9, 11/9
    21: [[14, 11], [13, 9], [11, 9]],
    
    # Цепь #22: 9/3, 11/3, 15/6, 14/8
    22: [[9, 3], [11, 3], [15, 6], [14, 8]],
    
    # Цепь #23: 17/9, 17/2, 15/5, 11/2, 17/11
    23: [[17, 9], [17, 2], [15, 5], [11, 2], [17, 11]],
    
    # Цепь #24: 13/11, 9/2, 3/5, 8/12, 17/10
    24: [[13, 11], [9, 2], [3, 5], [8, 12], [17, 10]],
    
    # Цепь #25: 7/11, 9/4, 5/9
    25: [[7, 11], [9, 4], [5, 9]],
    
    # Цепь #26: 9/8, 11/5, 1/1, 7/8, 6/13
    26: [[9, 8], [11, 5], [1, 1], [7, 8], [6, 13]],
    
    # Цепь #27: 3/2, 5/13, 12/4
    27: [[3, 2], [5, 13], [12, 4]],
    
    # Цепь #28: 7/2, 1/2, 15/1, 6/4
    28: [[7, 2], [1, 2], [15, 1], [6, 4]],
    
    # Цепь #29: 12/6, 5/6
    29: [[12, 6], [5, 6]],
    
    # Цепь #30: 11/6, 1/8, 10/11, 7/1
    30: [[11, 6], [1, 8], [10, 11], [7, 1]],
    
    # Цепь #31: 8/11, 4/12, 5/10, 11/11
    31: [[8, 11], [4, 12], [5, 10], [11, 11]],
    
    # Цепь #32: 10/2, 11/8, 9/5, 8/13, 5/8
    32: [[10, 2], [11, 8], [9, 5], [8, 13], [5, 8]],
    
    # Цепь #33: 3/12, 12/8, 12/10
    33: [[3, 12], [12, 8], [12, 10]],
    
    # Цепь #34: 13/12, 9/6, 3/3, 5/12, 13/4
    34: [[13, 12], [9, 6], [3, 3], [5, 12], [13, 4]],
    
    # Цепь #35: 12/5, 6/10, 15/12, 12/1
    35: [[12, 5], [6, 10], [15, 12], [12, 1]],
    
    # Цепь #36: 3/4, 5/1, 1/6, 7/9, 6/8
    36: [[3, 4], [5, 1], [1, 6], [7, 9], [6, 8]],
    
    # Цепь #37: 14/13, 3/13, 13/3, 9/1, 4/4
    37: [[14, 13], [3, 13], [13, 3], [9, 1], [4, 4]],
    
    # Цепь #38: 4/6, 15/10, 13/6, 4/10, 5/2
    38: [[4, 6], [15, 10], [13, 6], [4, 10], [5, 2]],
    
    # Цепь #39: 5/3, 7/4, 5/5, 6/1, 10/13
    39: [[5, 3], [7, 4], [5, 5], [6, 1], [10, 13]],
    
    # Цепь #40: 8/10, 12/9, 7/13, 6/3, 4/13
    40: [[8, 10], [12, 9], [7, 13], [6, 3], [4, 13]],
    
    # Цепь #41: 9/10, 13/8, 8/8
    41: [[9, 10], [13, 8], [8, 8]]
}

# nets that go to jst connector
jst_connections = [39, 34, 26, 40, 41, 3, 13, 24, 32, 5]

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
