# import KiCad libs
import os

os.environ["KICAD8_SYMBOL_DIR"] = "/usr/share/kicad/symbols/"
os.environ["KICAD_SYMBOL_DIR"] = "/usr/share/kicad/symbols/"
os.environ["KICAD7_SYMBOL_DIR"] = "/usr/share/kicad/symbols/"

from skidl import *

print("🔧 Creating DS7820 modules for Variant 50...")

# DS7820 - 19 модулей с реальными 14 пинами
modules = [Part("Interface_LineDriver", "DS8830", ref=f"U{i}") for i in range(1, 20)]

print(f"✅ Created {len(modules)} modules")

# JST connector - 12 pin (10 сигналов + VCC + GND)
print("🔌 Creating JST connector...")
connector = Part(
    "Connector_Generic",
    "Conn_01x12",
    ref="J1",
    footprint="Connector_JST:JST_XH_B12B-XH-A_1x12_P2.50mm_Vertical",
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
vcc_net += connector[11]  # JST pin 11 = VCC
gnd_net += connector[12]  # JST pin 12 = GND

print("✅ Power connected to all modules")

# НОВЫЕ данные из второго листа (вариант 50)
netlist_data = {
    1: [[7, 2], [17, 9], [19, 13]],
    2: [[15, 10], [7, 6], [19, 6], [6, 6], [14, 9]],
    3: [[19, 3], [19, 12]],
    4: [[18, 3], [19, 5], [19, 2], [17, 4], [18, 1]],
    5: [[1, 8], [19, 4], [6, 12]],
    6: [[18, 5], [19, 11]],
    7: [[16, 10], [17, 6], [8, 10], [10, 8]],
    8: [[7, 10], [13, 13], [2, 5], [13, 2], [2, 9]],
    9: [[11, 5], [18, 11], [18, 12], [11, 6], [19, 9]],
    10: [[17, 11], [11, 12], [3, 6], [17, 13], [19, 10]],
    11: [[10, 11], [19, 1], [14, 5], [19, 8], [4, 11]],
    12: [[8, 13], [14, 13]],
    13: [[13, 4], [5, 12], [14, 1], [14, 3], [18, 10]],
    14: [[16, 6], [2, 4], [14, 2]],
    15: [[10, 10], [3, 10], [18, 4], [9, 4], [14, 8]],
    16: [[15, 5], [9, 10], [12, 8], [15, 2], [13, 12]],
    17: [[8, 9], [11, 2], [14, 10], [13, 9], [8, 12]],
    18: [[13, 6], [7, 11]],
    19: [[2, 12], [11, 9], [1, 4], [10, 2], [18, 13]],
    20: [[13, 8], [18, 2], [16, 13], [18, 6], [2, 3]],
    21: [[15, 11], [8, 1], [15, 6], [11, 8]],
    22: [[16, 9], [2, 8], [16, 5], [1, 2], [10, 3]],
    23: [[9, 6], [8, 4]],
    24: [[5, 3], [15, 3], [14, 11]],
    25: [[2, 2], [2, 11], [7, 12], [13, 1], [17, 5]],
    26: [[16, 11], [5, 8], [16, 8], [11, 13], [15, 9]],
    27: [[13, 11], [17, 8], [4, 5], [13, 5], [7, 4]],
    28: [[5, 1], [5, 10], [8, 6], [15, 12], [15, 13]],
    29: [[10, 5], [10, 13], [15, 1], [15, 8], [3, 3]],
    30: [[16, 3], [14, 12], [1, 6], [11, 1], [16, 12]],
    31: [[13, 10], [2, 13], [17, 12]],
    32: [[18, 9], [12, 4]],
    33: [[4, 9], [16, 1], [10, 12]],
    34: [[7, 8], [13, 3], [2, 1], [17, 10], [15, 4]],
    35: [[17, 1], [17, 2], [11, 3], [9, 2], [18, 8]],
    36: [[2, 6], [10, 6], [12, 6], [17, 3], [3, 2]],
    37: [[8, 3], [8, 5], [9, 9], [9, 12], [16, 2]],
    38: [[9, 11], [12, 12], [5, 6], [10, 9], [4, 2]],
    39: [[6, 9], [16, 4], [4, 1], [14, 4], [6, 2]],
    40: [[2, 10], [12, 5], [11, 11], [6, 10], [6, 4]],
}

# Сети на разъём: 23, 13, 34, 2, 8, 39, 30, 15, 40, 4
jst_connections = [23, 13, 34, 2, 8, 39, 30, 15, 40, 4]

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
        nets[net_num] += connector[i + 1]  # JST pins 1-10
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
