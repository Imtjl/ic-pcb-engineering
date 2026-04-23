# import KiCad libs
import os

os.environ["KICAD8_SYMBOL_DIR"] = "/usr/share/kicad/symbols/"
os.environ["KICAD_SYMBOL_DIR"] = "/usr/share/kicad/symbols/"
os.environ["KICAD7_SYMBOL_DIR"] = "/usr/share/kicad/symbols/"

from skidl import *

print("🔧 Creating DS7820 modules for Variant 50-2...")

# 19 модулей с 14 пинами в корпусе SOIC
modules = [
    Part(
        "74xx", "74HC00", ref=f"U{i}", footprint="Package_SO:SOIC-14_3.9x8.7mm_P1.27mm"
    )
    for i in range(1, 20)
]

print(f"✅ Created {len(modules)} modules")

# connector - 12 pin (10 сигналов + VCC + GND)
print("🔌 Creating Molex connector...")
connector = Part(
    "Connector_Generic",
    "Conn_01x12",
    ref="J1",
    footprint="Connector_FFC-FPC:TE_1-84952-2_1x12-1MP_P1.0mm_Horizontal",
)

# Питание
print("⚡ Creating power nets...")
vcc_net = Net("VCC")
gnd_net = Net("GND")

# Подключаем питание ко всем модулям
for module in modules:
    vcc_net += module[14]  # VCC на pin 14
    gnd_net += module[7]  # GND на pin 7

# Подключаем питание к разъёму
vcc_net += connector[1]  # JST pin 1 = VCC
gnd_net += connector[12]  # JST pin 12 = GND

print("✅ Power connected to all modules")

netlist_data = {
    1: [[15, 13], [19, 8], [7, 2], [19, 9], [2, 10]],
    2: [[16, 11], [18, 4], [1, 10], [16, 6], [1, 1]],
    3: [[15, 9], [13, 1], [3, 12], [11, 2], [19, 2]],
    4: [[12, 2], [7, 8], [13, 8], [19, 4], [16, 12]],
    5: [[16, 9], [19, 12], [7, 13]],
    6: [[18, 13], [19, 3], [2, 3], [15, 6], [18, 2]],
    7: [[2, 2], [12, 10], [18, 3], [5, 2], [7, 4]],
    8: [[7, 12], [18, 5], [10, 11], [10, 8]],
    9: [[6, 5], [18, 1], [19, 5], [13, 3], [10, 9]],
    10: [[12, 6], [14, 8], [14, 11]],
    11: [[7, 9], [18, 6], [19, 1], [3, 2], [13, 6]],
    12: [[19, 13], [2, 13], [14, 2], [9, 13], [19, 6]],
    13: [[16, 2], [4, 8], [7, 6], [7, 3]],
    14: [[19, 10], [19, 11], [8, 11], [18, 8], [8, 6]],
    15: [[16, 13], [18, 11], [15, 2], [16, 8]],
    16: [[17, 3], [1, 11], [3, 10], [1, 2], [14, 6]],
    17: [[17, 6], [3, 9], [8, 1], [6, 10], [14, 9]],
    18: [[15, 5], [16, 1], [16, 4], [15, 11], [3, 3]],
    19: [[10, 5], [15, 3], [16, 5], [10, 12], [3, 13]],
    20: [[6, 3], [15, 1], [7, 11], [18, 10], [11, 12]],
    21: [[14, 12], [4, 4], [17, 2], [11, 8], [12, 1]],
    22: [[18, 9], [11, 1], [14, 3], [5, 10], [10, 3]],
    23: [[17, 1], [9, 10], [16, 3]],
    24: [[17, 10], [1, 3], [10, 4], [7, 10], [7, 1]],
    25: [[2, 9], [8, 4], [15, 8]],
    26: [[18, 12], [13, 13], [7, 5], [10, 6]],
    27: [[15, 10], [11, 11], [10, 13], [4, 1], [1, 9]],
    28: [[14, 10], [14, 13], [16, 10]],
    29: [[12, 13], [17, 8], [9, 3]],
    30: [[11, 10], [2, 5], [17, 13], [14, 4]],
    31: [[14, 5], [2, 1], [12, 4]],
    32: [[11, 4], [17, 11], [17, 12], [12, 11], [9, 6]],
    33: [[2, 12], [17, 9], [3, 11], [8, 5]],
    34: [[17, 5], [1, 4], [11, 13], [13, 4], [2, 6]],
    35: [[6, 12], [17, 4], [1, 12], [5, 6], [4, 10]],
    36: [[8, 10], [3, 5], [15, 4]],
    37: [[15, 12], [13, 10], [10, 1], [12, 12]],
    38: [[14, 1], [5, 3], [11, 6], [9, 5], [3, 8]],
    39: [[8, 12], [10, 2], [3, 6], [11, 9]],
}

jst_connections = [39, 31, 32, 13, 6, 5, 22, 14, 9, 25]

print("🕸️ Creating all nets with real pin numbers...")

nets = {}
for net_num, connections in netlist_data.items():
    net = Net(f"NET_{net_num}")

    for mod, pin in connections:
        if (
            mod <= len(modules) and 1 <= pin <= 14 and pin not in [7, 14]
        ):  # Исключаем VCC/GND
            net += modules[mod - 1][pin]

    nets[net_num] = net
    print(f"✅ NET_{net_num}: {len(net.pins)} connections")

print(f"\n🔌 Connecting nets to JST connector...")

for i, net_num in enumerate(jst_connections):
    if net_num in nets:
        nets[net_num] += connector[i + 2]  # JST pins 2-11
        print(f"✅ NET_{net_num} → JST pin {i+1}")

print(f"\n💾 Generating netlist...")
generate_netlist(file_="variant_50.net")

print(f"\n🎉 Done!")
print(f"📊 Stats:")
print(f"  Modules: {len(modules)}")
print(f"  Signal nets: {len(nets)}")
print(f"  Power nets: VCC, GND")
print(f"  JST connections: {len(jst_connections)} + VCC + GND")
print(f"  File: variant_50.net")

print(f"\n💡 Import variant_50.net into KiCad PCB editor:")
print(f"  Tools → Update PCB from Schematic → Import Netlist")
