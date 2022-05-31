#!/usr/bin/env python3
import math
if __import__("sys").platform != "win32":
    import readline

# 表示圆周率的字符
pi_s = chr(960)
# 特殊的三角方程的解集
special = {
    "s": {
        -1: "2k%s - %s/2" % (pi_s, pi_s),
        0: "k" + pi_s,
        1: "2k%s + %s/2" % (pi_s, pi_s)
    },
    "c": {
        -1: "2k%s + %s" % (pi_s, pi_s),
        0: "k%s + %s/2" % (pi_s, pi_s),
        1: "2k" + pi_s
    },
    "t": {
        0: "k" + pi_s
    }
}
# 单位圆的弧度圈，逆时针方向，从-pi/2开始
# 为什么是-pi/2而非0呢？很简单，cos(x)>a需要纵截单位圆，这样便于程序设计，且也便于sin(x)>a的运算
unit_circle = [
        -math.pi / 2,
        -math.pi / 3,
        -math.pi / 4,
        -math.pi / 6,
        0,
        math.pi / 6,
        math.pi / 4,
        math.pi / 3,
        math.pi / 2,
        2 * math.pi / 3,
        3 * math.pi / 4,
        5 * math.pi / 6,
        math.pi,
        7 * math.pi / 6,
        5 * math.pi / 4,
        4 * math.pi / 3
]

def get_rad(value, always_p=False):
    """返回一个弧度字符串（a*pi/b，范围从-30pi到30pi，且局限性大）

    @param value 某浮点数
    @param always_p 返回的弧度是否为正，若为True则返回5pi/3而非-pi/3
    """
    if value == 0: return "0"
    if math.isclose(math.pi, value): return pi_s
    if math.isclose(2 * math.pi, value): return "2" + pi_s
    for a in [2, 3, 4, 6, 12]:
        for b in range(-60, 61):
            if math.isclose(b * math.pi / a, value):
                if always_p:
                    return "%s%s/%d" % (b if abs(b) != 1 else str(b).replace("1", ""), pi_s, a)
                else:
                    if math.isclose(2 * math.pi - math.pi / 3, value):
                        return "-" + pi_s + "/3"
                    elif math.isclose(2 * math.pi - math.pi / 4, value):
                        return "-" + pi_s + "/4"
                    elif math.isclose(2 * math.pi - math.pi / 6, value):
                        return "-" + pi_s + "/6"
                    else:
                        return "%s%s/%d" % (b if abs(b) != 1 else str(b).replace("1", ""), pi_s, a)

def get_trig(name, value):
    """返回一个三角比的值对应的弧度（一般情况下是两个）

    @param name 三角比的名称（"s", "c", "t"）
    @param value 三角比的值
    """
    if name == "s": f = math.sin
    if name == "c": f = math.cos
    if name == "t": f = math.tan
    result = []
    for i in unit_circle:
        # 对精度不足的修复：math.isclose(math.sin(math.pi), 0) => False
        # 但是由于精度不够（接近于0的数加上1就更接近于1了）：math.isclose(math.sin(math.pi) + 1, 1) => True
        if math.isclose(value, f(i)) or math.isclose(value + 1, f(i) + 1):
            result.append([get_rad(i), i])
    return result

def get_num(s):
    flag = 1
    if s[0] == "-":
        flag = -1
        s = s[1:]
    if s.startswith("sqrt(") and s[-1] == ")":
        return flag * math.sqrt(float(s[5:-1]))
    else:
        return flag * float(s)

def get_value(s):
    a, b = 0, 0
    if "/" in s:
        a, b = [get_num(n) for n in s.split("/", 1)]
    else:
        a, b = get_num(s), 1
    return a / b

def format_string(s):
    v = get_value(s)
    if getattr("", "removeprefix", None) is None:
        s = s.replace("-", "")
        if v < 0:
            s = "-" + s
        return s
    if "/" not in s:
        return s
    else:
        a, b = s.split("/")
        if v == int(v):
            return str(int(v))
        if v > 0:
            return "%s/%s" % (a.removeprefix("-"), b.removeprefix("-"))
        elif v < 0:
            return "%s/%s" % ("-" + a.removeprefix("-"), b.removeprefix("-"))

def equ(name, s):
    """求解三角方程

    @param name 三角比名
    @param s 值
    """
    name, s = name.strip(), s.strip()
    if name == "s": f = math.asin
    elif name == "c": f = math.acos
    elif name == "t": f = math.atan
    else: return
    try:
        value = get_value(s)
        s = format_string(s)
    except:
        print("Error: An invalid number!")
        return
    try:
        a = f(value)
    except ValueError:
        print("Error: Domain error!")
        return
    # 寻找特殊解
    for tn, kv in special.items():
        if name == tn:
            for k, v in kv.items():
                if math.isclose(k, value):
                    print("x = %s" % v)
                    return
    if (v := get_rad(a)) is not None:
        # 可使用弧度表示的解集
        if name == "s":
            if a > 0:
                print("x = k%s + (-1)^k * %s" % (pi_s, v))
            elif  a < 0:
                print("x = k%s - (-1)^k * %s" % (pi_s, v[1:]))
        elif name == "c":
            print("x = 2k%s %s %s" % (pi_s, chr(177), v))
        elif name == "t":
            if a > 0:
                print("x = k%s + %s" % (pi_s, v))
            elif a < 0:
                print("x = k%s - %s" % (pi_s, v[1:]))
    else:
        # 如上述方法不可行，则使用反三角表示
        if name == "s":
            if a > 0:
                print("x = k%s + (-1)^k * arcsin(%s)" % (pi_s, s))
            elif a < 0:
                print("x = k%s - (-1)^k * arcsin(%s)" % (pi_s, s[1:]))
        elif name == "c":
            print("x = 2k%s %s arccos(%s)" % (pi_s, chr(177), s))
        elif name == "t":
            if a > 0:
                print("x = k%s + arctan(%s)" % (pi_s, s))
            elif a < 0:
                print("x = k%s - arctan(%s)" % (pi_s, s[1:]))

def inequ(name, s, op):
    """求解三角不等式

    @param name 三角比名
    @param s 值
    @param op 不等号
    """
    name, s = name.strip(), s.strip()
    if name == "s": f = math.asin
    elif name == "c": f = math.acos
    elif name == "t": f = math.atan
    else: return
    try:
        value = get_value(s)
    except:
        print("Error: An invalid number!")
        return
    try:
        a = f(value)
    except ValueError:
        print("Error: Domain error!")
        return
    # sin和cos较麻烦，除了最后的print就别想看懂了
    if name == "s":
        if math.isclose(abs(value), 1):
            # 根据图像可知，y=sin(x)没有一点的函数值大于1
            print("No solution")
            return
        x1, x2 = get_trig("s", value)
        if (op == "<"):
            x1, x2 = x2, x1
            if value > 0:
                x1 = [get_rad(-math.tau + x1[1], True), -math.tau + x1[1]]
            elif value < 0:
                x2 = [get_rad(x2[1] + math.tau, True), x2[1] + math.tau]
        if (op == "<") and math.isclose(value, 0):
            # sin(x)<0
            print("(2k%s-%s, 2k%s)" % ((pi_s, ) * 3))
            return
        print("(2k%s%s%s, 2k%s%s%s)" % (pi_s, "+" if x1[1] > 0 else "", x1[0] if x1[1] != 0 else "", pi_s, "+" if x2[1] > 0 else "", x2[0]))
    if name == "c":
        if math.isclose(abs(value), 1):
            # 同上，y=cos(x)亦没有一点的函数值大于1
            print("No solution")
            return
        x1, x2 = get_trig("c", value)
        if (op == "<") and (value > 0) and (x2[1] > x1[1]):
                x1, x2 = x2, x1
                x2 = [get_rad(x2[1] + math.tau, True), x2[1] + math.tau]
        elif (op == ">") and (value < 0):
                x1, x2 = x2, x1
                x1 = [get_rad(-math.tau + x1[1], True), -math.tau + x1[1]]
        if (op == "<") and math.isclose(value, 0):
            # cos(x)<0
            print("(2k%s+%s/2, 2k%s+3%s/2)" % ((pi_s, ) * 4))
            return
        print("(2k%s%s%s, 2k%s%s%s)" % (pi_s, "+" if x1[1] >= 0 else "", x1[0], pi_s, "+" if x2[1] > 0 else "", x2[0]))
    if name == "t":
        # tan最简单，看函数图像即可出结果
        if op == ">":
            print("(k%s%s%s, k%s+%s/2)" % (pi_s, "+" if a >= 0 else "", get_rad(a), pi_s, pi_s))
        elif op == "<":
            print("(k%s+%s/2, k%s%s%s)" % (pi_s, pi_s, pi_s, "+" if a >= 0 else "", get_rad(a)))

if __name__ == "__main__":
    while True:
        expr = input("expr: ")
        if "=" in expr:
            equ(*expr.split("=")[:2])
        elif ">" in expr:
            inequ(*expr.split(">")[:2], ">")
        elif "<" in expr:
            inequ(*expr.split("<")[:2], "<")
        elif expr == "q":
            exit()
