import math


def init():
    r1 = 15000
    d1 = 10
    w1 = 0.005

    r2 = 1200
    d2 = 20
    w2 = 0.01

    r3 = 1500
    d3 = 20
    w3 = 0.01

    r4 = 5600
    d4 = 10
    w4 = 0.01

    r5 = 300
    d5 = 10
    w5 = 0.005

    global ri, ri_rev, di, wi, w0
    ri = [r1, r2, r3, r4, r5]
    ri_rev = [x ** (-1) for x in ri]
    di = [determine_precision(x) for x in [d1, d2, d3, d4, d5]]
    wi = [w1, w2, w3, w4, w5]
    w0 = 2

    global ci, smin
    ci = [1000, 510]
    smin = 0.5 * 0.5 * 0.01


def determine_precision(delta):
    if delta == 10:
        return 0.3
    if delta == 20:
        return 0.2
    return Nan


def calc():
    print("#1. Calculate film resistors\n")

    p_optimal_raw = math.sqrt(sum(ri) / sum(ri_rev))
    p_optimal = round(p_optimal_raw, -2)
    print(f"Optimal criteria: {p_optimal} Ohm/□")

    print("\n-> Film resistors form coefficients:")
    ki = [round(x / p_optimal, 3) for x in ri]
    for i, k in enumerate(ki, start=1):
        print(f"Kf_{i} = {k}")

    print("\n-> Width bi >= max(bwi; b_precise):")
    bi = [round(math.sqrt((p_optimal * w) / (r * w0)) * 10, 3) for r, w in zip(ri, wi)]
    b_res = [math.ceil(max(b, d) * 10) / 10 for b, d in zip(bi, di)]
    for i, (b, d, br) in enumerate(zip(bi, di, b_res), start=1):
        print(f"b_{i} = {br} mm >= max[bw_{i} = {b} mm; b_precise = {d} mm]")

    print(f"\n?? All kf_i < 10: {all(x < 10 for x in ki)}")
    print("-> Calculate Length li:")

    li = [round(k * b, 1) for k, b in zip(ki, b_res)]
    for i, l in enumerate(li, start=1):
        print(f"l_{i} = {l} mm")

    print("\nWith calculation error:")
    rs = [round(l * p_optimal / b, 2) for l, b in zip(li, b_res)]
    rd = [round(abs(r - rs) / r, 2) * 100 for r, rs in zip(ri, rs)]
    for i, (l, rs, rd) in enumerate(zip(li, rs, rd), start=1):
        print(f"l_{i} = {l} mm; R'_{i} = {rs}; ∆R' = {rd}%")

    print("\n#2. Calculate film capasitors\n")

    print("Choose appropriate material:")
    for i, c in enumerate(ci, start=1):
        print(f"Co*_{i} = C_{i}/Smin = {c}/{smin} = {c/smin/1000}*10^3 Пф/см^2")

    c0 = 200 * 10**3
    print(f"=> Пятиокись тантала: Co = {c0/10**3}*10^3 Пф/см^2\n")

    print("Calculate active area S:")
    si = [c / c0 * 100 for c in ci]
    for i, (c, s) in enumerate(zip(ci, si), start=1):
        print(f"S_{i} = C_{i}/Co = {c}/{c0} = {s} mm^2")

    print(f"\n?? 0.1 <= S <= 1 mm^2: {all(s >= 0.1 and s <= 1 for s in si)}")
    print("=> Using configuration 4.7в")


if __name__ == "__main__":
    init()
    calc()
