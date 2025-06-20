# import KiCad libs
import os

os.environ["KICAD8_SYMBOL_DIR"] = "/usr/share/kicad/symbols/"
os.environ["KICAD_SYMBOL_DIR"] = "/usr/share/kicad/symbols/"
os.environ["KICAD7_SYMBOL_DIR"] = "/usr/share/kicad/symbols/"

from skidl import *

print("🔧 Creating DS7820 modules for new variant...")

# DS7820 - 19 модулей с реальными 14 пинами
modules = [Part("Interface_LineDriver", "DS7820", ref=f"U{i}") for i in range(1, 20)]

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

# НОВЫЕ данные из третьего листа
netlist_data = {
    1: [[19, 1], [2, 3], [3, 1], [19, 9], [13, 5]],
    2: [[12, 10], [11, 5], [17, 3], [15, 5], [14, 12]],
    3: [[11, 3], [18, 3], [3, 13], [16, 6], [1, 1]],
    4: [[19, 5], [19, 13], [19, 11]],
    5: [[19, 10], [6, 5], [18, 6], [13, 4]],
    6: [[17, 13], [19, 8]],
    7: [[18, 1], [5, 1], [15, 9], [10, 5]],
    8: [[18, 11], [4, 8], [10, 2], [19, 3], [6, 6]],
    9: [[3, 6], [9, 11], [15, 1], [15, 2], [13, 6]],
    10: [[19, 4], [18, 8], [7, 8], [5, 11]],
    11: [[15, 6], [19, 2]],
    12: [[3, 2], [2, 11], [14, 2], [5, 4], [15, 11]],
    13: [[19, 6], [16, 13], [2, 5]],
    14: [[18, 9], [14, 13], [19, 12], [16, 10], [16, 3]],
    15: [[7, 2], [16, 2], [2, 10], [8, 4]],
    16: [[5, 5], [13, 9], [4, 11], [3, 9]],
    17: [[17, 4], [1, 4], [2, 9], [12, 2], [16, 8]],
    18: [[5, 2], [8, 1], [18, 13], [10, 11]],
    19: [[16, 5], [18, 4], [12, 11], [7, 12]],
    20: [[4, 13], [5, 6], [18, 2], [4, 5], [9, 8]],
    21: [[7, 13], [7, 3], [3, 5], [6, 13], [1, 11]],
    22: [[4, 4], [11, 1], [2, 1], [18, 12], [14, 6]],
    23: [[9, 13], [4, 3], [4, 1], [9, 10], [5, 10]],
    24: [[18, 10], [16, 12]],
    25: [[16, 11], [14, 4], [13, 12]],
    26: [[7, 9], [3, 11], [18, 5], [1, 9], [7, 10]],
    27: [[15, 4], [13, 11], [17, 10], [10, 6], [17, 2]],
    28: [[14, 9], [11, 8], [11, 10], [6, 2], [10, 9]],
    29: [[9, 12], [9, 4], [8, 10], [14, 10], [7, 5]],
    30: [[5, 13], [17, 11], [2, 8], [11, 2]],
    31: [[14, 1], [15, 10], [3, 4], [9, 1], [12, 5]],
    32: [[3, 12], [5, 8], [12, 8], [5, 9], [12, 4]],
    33: [[9, 3], [17, 1]],
    34: [[13, 2], [13, 10], [10, 10], [16, 9]],
    35: [[15, 3], [17, 5], [1, 2]],
    36: [[6, 4], [13, 1], [2, 13], [5, 3], [8, 6]],
    37: [[11, 6], [1, 8], [8, 5], [7, 4]],
    38: [[14, 5], [17, 6], [9, 5], [8, 3], [9, 6]],
    39: [[8, 2], [13, 8], [15, 13], [12, 1], [16, 1]],
    40: [[10, 3], [4, 6], [7, 1]],
}

# Сети на разъём: 39, 40, 36, 18, 19, 34, 25, 35, 29, 20
jst_connections = [39, 40, 36, 18, 19, 34, 25, 35, 29, 20]

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
generate_netlist(file_="variant_new.net")

print(f"\n🎉 Done!")
print(f"📊 Stats:")
print(f"  Modules: {len(modules)}")
print(f"  Signal nets: {len(nets)}")
print(f"  Power nets: VCC, GND")
print(f"  JST connections: {len(jst_connections)} + VCC + GND")
print(f"  Total connections: 168")
print(f"  File: variant_new.net")

print(f"\n💡 Import variant_new.net into KiCad PCB editor:")
print(f"  Tools → Update PCB from Schematic → Import Netlist")
print(f"\n🎯 Next step: OCR automation!")
