#!/usr/bin/env python3
import math
if __import__("sys").platform != "win32":
    import readline

# 定义域，通过set_var函数修改
D = None
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
    else:
        return str(value)

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

def equ(name, s):
    """求解三角方程

    @param name 三角比名
    @param s 值
    """
    global D
    name, s = name.strip(), s.strip()
    if name == "sin": f = math.asin; name = "s"
    elif name == "cos": f = math.acos; name = "c"
    elif name == "tan": f = math.atan; name = "t"
    else: return
    try:
        # 我就不再写一个解析器了，直接用就可以了
        value = float(eval(s, {"sqrt": math.sqrt, "pi": math.pi, "__builtins__": {}}))
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
            formula = ["k * math.pi + (-1) ** k * %s" % a]
            if a > 0:
                print("x = k%s + (-1)^k * %s" % (pi_s, v))
            elif a < 0:
                print("x = k%s - (-1)^k * %s" % (pi_s, v[1:]))
        elif name == "c":
            formula = ["k * math.tau + %s" % a, "k * math.tau + %s" % a]
            print("x = 2k%s %s %s" % (pi_s, chr(177), v))
        elif name == "t":
            formula = ["k * math.pi + %s" % a]
            if a > 0:
                print("x = k%s + %s" % (pi_s, v))
            elif a < 0:
                print("x = k%s - %s" % (pi_s, v[1:]))
        # 如若设置了定义域，那么就在定义域内找解
        if D is not None:
            result = []
            for expr in formula:
                if (D[0] <= (x := eval(expr.replace("k", "(0)"))) <= D[1]):
                    result.append(get_rad(x))
                i, flag = 1, 1
                while True:
                    if (D[0] <= (x := eval(expr.replace("k", "(%s)" % i))) <= D[1]):
                        if get_rad(x) not in result:
                            result.append(get_rad(x))
                        i += flag * 1
                    else:
                        if flag == -1: break
                        i, flag = 1, -1
            print("Solution in D: {%s}" % ", ".join(result))
            D = None
    else:
        # 如上述方法不可行，则使用反三角表示
        if name == "s":
            print("x = k%s + (-1)^k * arcsin(%s)" % (pi_s, s))
        elif name == "c":
            print("x = 2k%s %s arccos(%s)" % (pi_s, chr(177), s))
        elif name == "t":
            print("x = k%s + arctan(%s)" % (pi_s, s))

def inequ(name, s, op):
    """求解三角不等式

    @param name 三角比名
    @param s 值
    @param op 不等号
    """
    name, s = name.strip(), s.strip()
    if name == "sin": f = math.asin; name = "s"
    elif name == "cos": f = math.acos; name = "c"
    elif name == "tan": f = math.atan; name = "t"
    else: return
    try:
        value = float(eval(s, {"sqrt": math.sqrt, "pi": math.pi, "__builtins__": {}}))
    except:
        print("Error: An invalid number!")
        return
    try:
        a = f(value)
    except ValueError:
        print("Error: Domain error!")
        return
    # 根据不等号设置区间开闭
    get_open = lambda: "(" if "=" not in op else "["
    get_close = lambda: ")" if "=" not in op else "]"
    # sin和cos较麻烦，除了最后的print就别想看懂了
    if name == "s":
        x1, x2 = get_trig("s", value)
        if ("<" in op):
            x1, x2 = x2, x1
            if value > 0:
                x1 = [get_rad(-math.tau + x1[1], True), -math.tau + x1[1]]
            elif value < 0:
                x2 = [get_rad(x2[1] + math.tau, True), x2[1] + math.tau]
        if ("<" in op) and math.isclose(value, 0):
            # sin(x)<0
            print("%s2k%s-%s, 2k%s%s" % ((get_open(), ) + (pi_s, ) * 3) + (get_close(), ))
            return
        print("%s2k%s%s%s, 2k%s%s%s%s" % (get_open(), pi_s, "+" if x1[1] > 0 else "", x1[0] if x1[1] != 0 else "", pi_s, "+" if x2[1] > 0 else "", x2[0], get_close()))
    if name == "c":
        x1, x2 = get_trig("c", value)
        if ("<" in op) and (value > 0) and (x2[1] > x1[1]):
                x1, x2 = x2, x1
                x2 = [get_rad(x2[1] + math.tau, True), x2[1] + math.tau]
        elif (">" in op) and (value < 0):
                x1, x2 = x2, x1
                x1 = [get_rad(-math.tau + x1[1], True), -math.tau + x1[1]]
        if ("<" in op) and math.isclose(value, 0):
            # cos(x)<0
            print("%s2k%s+%s/2, 2k%s+3%s/2%s" % ((get_open(), ) + (pi_s, ) * 4) + (get_close(), ))
            return
        print("%s2k%s%s%s, 2k%s%s%s%s" % (get_open(), pi_s, "+" if x1[1] >= 0 else "", x1[0], pi_s, "+" if x2[1] > 0 else "", x2[0], get_close()))
    if name == "t":
        # tan最简单，看函数图像即可出结果
        if ">" in op:
            print("%sk%s%s%s, k%s+%s/2)" % (get_open(), pi_s, "+" if a >= 0 else "", get_rad(a), pi_s, pi_s))
        elif "<" in op:
            print("(k%s+%s/2, k%s%s%s%s" % (pi_s, pi_s, pi_s, "+" if a >= 0 else "", get_rad(a), get_close()))

def set_var(name, *args):
    global D
    if name == "D":
        if len(args) == 2:
            try:
                s, e = [float(eval(s, {"sqrt": math.sqrt, "pi": math.pi, "__builtins__": {}})) for s in args]
                if s > e:
                    s, e = e, s
                D = [s, e]
            except:
                print("Error: An invalid number!")

if __name__ == "__main__":
    while True:
        cmd = input(">>> ").split(" ", 1)
        if len(cmd) == 1:
            action = cmd[0]
            if action == "q":
                exit()
        else:
            action, args = cmd
            if action == "do":
                if ("=" in args) and (">=" not in args) and ("<=" not in args):
                    equ(*args.split("=")[:2])
                elif (">" in args) and (">=" not in args):
                    inequ(*args.split(">", 1), ">")
                elif (">=" in args):
                    inequ(*args.split(">=", 1), ">=")
                elif ("<" in args) and ("<=" not in args):
                    inequ(*args.split("<", 1), "<")
                elif ("<=" in args):
                    inequ(*args.split("<=", 1), "<")
            elif action == "set":
                set_var(*args.split(" "))
