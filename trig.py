#!/usr/bin/env python3
# MIT License
#
# Copyright (c) 2022 jason-bowen-zheng
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.

from fractions import Fraction
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
    """返回一个弧度字符串（a*pi/b）

    @param value 某浮点数
    @param always_p 返回的弧度是否为正，若为True则返回5pi/3而非-pi/3
    """
    if value == 0: return "0"
    frac = Fraction(value / math.pi).limit_denominator(1000)
    a, b = frac.as_integer_ratio()
    if math.isclose(value, frac * math.pi):
        if always_p:
            return "%s%s/%s" % (a if abs(a) != 1 else str(a).replace("1", ""), pi_s, b)
        else:
            if math.isclose((a + 1) / b, 2):
                return "-%s/%s" % (pi_s, b)
            else:
                return "%s%s/%s" % (a if abs(a) != 1 else str(a).replace("1", ""), pi_s, b)
    else:
        if math.isclose(value, frac):
            return "%s%s%s" % (a, "/" if b == 1 else "", b)
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

def trig_eval(s):
    # 解析器就不写了，直接用就可以了
    return eval(s, {"sqrt": math.sqrt, "pi": math.pi, "__builtins__": {}})

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
        value = float(trig_eval(s))
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
    if (v := get_rad(a)).find(pi_s) != -1:
        # 可使用弧度表示的解集
        if name == "s":
            formula = ["k * math.pi + (-1) ** k * %s" % a]
            if a > 0:
                print("x = k%s + (-1)^k * %s" % (pi_s, v))
            elif a < 0:
                print("x = k%s - (-1)^k * %s" % (pi_s, get_rad(-a)))
        elif name == "c":
            formula = ["k * math.tau + %s" % a, "k * math.tau + %s" % a]
            print("x = 2k%s %s %s" % (pi_s, chr(177), v))
        elif name == "t":
            formula = ["k * math.pi + %s" % a]
            if a > 0:
                print("x = k%s + %s" % (pi_s, v))
            elif a < 0:
                print("x = k%s - %s" % (pi_s, get_rad(-a)))
        # 如若设置了定义域，那么就在定义域内找解
        if D is not None:
            first, last, result = 0, 0, []
            for expr in formula:
                if (D[0] <= (x := eval(expr.replace("k", "(0)"))) <= D[1]):
                    result.append(get_rad(x))
                    first, last = x, x
                i, flag = 1, 1
                while True:
                    if (D[0] <= (x := eval(expr.replace("k", "(%s)" % i))) <= D[1]):
                        if get_rad(x) not in result:
                            if x > last:
                                result.append(get_rad(x))
                                last = x
                            elif x < first:
                                result.insert(0, get_rad(x))
                                first = x
                        i += flag * 1
                    else:
                        if flag == -1: break
                        i, flag = 1, -1
            print("Solution in D: {%s}" % ", ".join(result))
            D = None
    else:
        # 如上述方法不可行，则使用反三角表示，反三角不支持寻找定义域内的解
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
        value = float(trig_eval(s))
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
    # sin和cos较麻烦，除了最后的print就别想看懂了（尽管有很多注释，但是不借助单位圆绝对无法理解）
    if name == "s":
        if abs(value) == 1:
            # 对于极值的处理
            if (op == ">=") and (value == 1): print("x = 2k%s + %s" % (pi_s, pi_s))
            elif (op == ">=") and (value == -1): print("x = R")
            elif (op == ">") and (value == 1): print("x = %s" % chr(8709))
            elif (op ==">") and (value == -1): print("x %s 2k%s + 3%s/2" % (chr(8800), pi_s, pi_s))
            return
        x1, x2 = get_trig("s", value)
        if ("<" in op):
            # 解集是逆时针找出的，需对调始终边
            x1, x2 = x2, x1
            if value > 0:
                # 此时解集穿过x轴正半轴，需表示成(2*k*pi-a, 2*k*pi+b)
                x1 = [get_rad(-math.tau + x1[1], True), -math.tau + x1[1]]
            elif value < 0:
                # 此时终小于始，需调整
                x2 = [get_rad(x2[1] + math.tau, True), x2[1] + math.tau]
        if value == 0:
            print("%s2k%s-%s, 2k%s%s" % ((get_open(), ) + (pi_s, ) * 3) + (get_close(), ))
        else:
            print("%s2k%s%s%s, 2k%s%s%s%s" % (get_open(), pi_s, "+" if x1[1] > 0 else "", x1[0] if x1[1] != 0 else "", pi_s, "+" if x2[1] > 0 else "", x2[0], get_close()))
    if name == "c":
        if abs(value) == 1:
            if (op == ">=") and (value == 1): print("x = 2k%s" % pi_s)
            elif (op == ">=") and (value == -1): print("x = R")
            elif (op == ">") and (value == 1): print("x = %s" % chr(8709))
            elif (op ==">") and (value == -1): print("x %s 2k%s + %s" % (chr(8800), pi_s, pi_s))
            return
        x1, x2 = get_trig("c", value)
        if ("<" in op) and (value > 0):
            # 此时解集为第一象限始边到第四象限终边，但由于上述单位圆特性，需对调始终边
            x1, x2 = x2, x1
            x2 = [get_rad(x2[1] + math.tau, True), x2[1] + math.tau]
        elif (">" in op) and (value < 0):
            # 此时解集穿过x轴正半轴
            x1, x2 = x2, x1
            x1 = [get_rad(-math.tau + x1[1], True), -math.tau + x1[1]]
        if ("<" in op) and (value == 0):
            print("%s2k%s+%s/2, 2k%s+3%s/2%s" % ((get_open(), ) + (pi_s, ) * 4) + (get_close(), ))
        else:
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
                s, e = [float(trig_eval(s)) for s in args]
                if s > e:
                    s, e = e, s
                D = [s, e]
            except:
                print("Error: An invalid number!")
    else:
        print("Error: No variable named \"%s\"!" % name)

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
