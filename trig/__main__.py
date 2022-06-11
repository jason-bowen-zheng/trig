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

from .cas import *
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
    "sin": {
        -1: {"2*k%s" % pi_s: True, "-": False,math.pi / 2: True},
        0: {"k" + pi_s: True},
        1: {"2*k%s" % pi_s: True, "+": False, math.pi / 2: True}
    },
    "cos": {
        -1: {"2*k%s" % pi_s: True, "+": False, math.pi: True},
        0: {"k%s" % pi_s: True, "+": False, math.pi / 2: True},
        1: {"2*k" + pi_s: True}
    },
    "tan": {
        0: {"k" + pi_s: True}
    }
}
# 单位圆的弧度圈，逆时针方向，从-pi/2开始
# 为什么是-pi/2而非0呢？很简单，cos(x)>a需要纵截单位圆，这样便于程序设计，且也便于sin(x)>a的运算（横截的话左右对称）
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

def get_trig(name, value):
    """返回一个三角比的值对应的弧度（一般情况下是两个）

    @param name  三角比的名称（"s", "c", "t"）
    @param value 三角比的值
    """
    if name[0] == "s": f = math.sin
    if name[0] == "c": f = math.cos
    if name[0] == "t": f = math.tan
    result = []
    for i in unit_circle:
        # 对精度不足的修复：math.isclose(math.sin(math.pi), 0) => False
        # 但是由于精度不够（接近于0的数加上1就更接近于1了）：math.isclose(math.sin(math.pi) + 1, 1) => True
        if math.isclose(value, f(i)) or math.isclose(value + 1, f(i) + 1):
            result.append([get_num_string(i), i])
    return result

def trig_eval(s, left=False):
    """解析输入的表达式

    @param s    某表达式
    @param left 是否为等号左边的表达式
    """
    if left:
        if s == "s": return Sine(Variable())
        elif s == "c": return Cosine(Variable())
        elif s == "t": return Tangent(Variable())
        s = s.replace("x", "x()")
        return eval(s, {"cos": lambda x: Cosine(x), "sin": lambda x: Sine(x),
            "sqrt": math.sqrt, "pi": math.pi, "tan": lambda x: Tangent(x),
            "x": lambda: Variable(), "__builtins__": {}})
    else:
        return eval(s, {"sqrt": math.sqrt, "pi": math.pi, "__builtins__": {}})

def build_sol(expr, left):
    """根据左值和最简方程的解构建最终解

    @param expr 包含解的字典
    @param left 左值
    """
    x_coeff = left.args[0].args[0] if isinstance(left.args[0], Mul) else 1
    result = []
    for item, action in expr.items():
        if action == False:
            result.append(item)
        else:
            if isinstance(item, (int, float)):
                result.append(get_num_string(item / x_coeff))
            else:
                if "*" in item:
                    coeff, item = item.split("*")
                else:
                    coeff = 1
                a, b = Fraction(float(coeff) / x_coeff).limit_denominator(1000).as_integer_ratio()
                result.append("%s%s%s%s" % (a if abs(a) != 1 else str(a).replace("1", ""), item,
                    "/" if b != 1 else "", "" if b == 1 else b))
    return " ".join(result)

def is_simplest(expr):
    if not isinstance(expr, Function):
        raise RuntimeError()
    elif isinstance(expr.args[0], Variable):
        return True
    elif isinstance(expr.args[0], Mul):
        if len(expr.args[0].args) == 2:
            if isinstance(expr.args[0].args[1], Variable):
                return True
    return False

def equ(expr, val):
    """求解三角方程

    @param expr 等号左边的表达式
    @param val  值
    """
    global D
    try:
        left = trig_eval(expr, True)
        if not is_simplest(left):
            print("ERROR: Only support simplest trigonometric equation!")
            return
    except:
        print("Error: Invalid left expr!")
        return
    if left.name == "sin": f = math.asin
    elif left.name == "cos": f = math.acos
    elif left.name == "tan": f = math.atan
    try:
        val = float(trig_eval(val))
        sol = f(val)
    except ValueError:
        print("Error: Invalid right value!")
        return
    # 寻找特殊解
    for tn, kv in special.items():
        if left.name == tn:
            for k, v in kv.items():
                if math.isclose(k, val):
                    print("x = %s" % build_sol(v, left))
                    return
    if get_num_string(sol).find(pi_s) != -1:
        # 可使用弧度表示的解集
        coeff = left.args[0].args[0] if isinstance(left.args[0], Mul) else 1
        if left.name == "sin":
            formula = ["(k * math.pi + (-1) ** k * %s) %s" % (sol, ("/ (%s)" % coeff) if coeff != 1 else "")]
            print("x = " + build_sol({
                "k%s" % pi_s: True,
                "+" if sol > 0 else "-": False,
                "(-1)**k": False,
                "*": False,
                abs(sol): True
            }, left))
        elif left.name == "cos":
            formula = ["(k * math.tau + %s) %s" % (sol, ("/ (%s)" % coeff) if coeff != 1 else ""),
                    "(k * math.tau - %s) %s" % (sol, ("/ (%s)" % coeff) if left.coeff != 1 else "")]
            print("x = " + build_sol({
                "2*k%s" % pi_s: True,
                chr(177): False,
                sol: True,
            }, left))
        elif left.name == "tan":
            formula = ["(k * math.pi + %s) %s" % (sol, ("/ (%s)" % coeff) if coeff != 1 else "")]
            print("x = " + build_sol({
                "k%s" % pi_s: True,
                "+" if sol > 0 else "-": False,
                abs(sol): True,
            }, left))
        # 如若设置了定义域，那么就在定义域内找解
        if D is not None:
            first, last, result = 0, 0, []
            for expr in formula:
                if (D[0] <= (x := eval(expr.replace("k", "(0)"))) <= D[1]):
                    result.append(get_num_string(x))
                    first, last = x, x
                i, flag = 1, 1
                while True:
                    if (D[0] <= (x := eval(expr.replace("k", "(%s)" % i))) <= D[1]):
                        if get_num_string(x) not in result:
                            if x > last:
                                result.append(get_num_string(x))
                                last = x
                            elif x < first:
                                result.insert(0, get_num_string(x))
                                first = x
                        i += flag * 1
                    else:
                        if flag == -1: break
                        i, flag = 1, -1
            print("Solution in D: {%s}" % ", ".join(result))
            D = None
    else:
        # 如上述方法不可行，则使用反三角表示，反三角不支持寻找定义域内的解
        if left.name == "sin":
            print("x = " + build_sol({
                "k%s" % pi_s: True,
                "+" if sol > 0 else "-": False,
                "(-1)**k": False,
                "*": False,
                "arcsin(%s)" % get_num_string(abs(val)): True
            }, left))
        elif left.name == "cos":
            print("x = " + build_sol({
                "2*k%s" % pi_s: True,
                chr(177): False,
                "arccos(%s)" % get_num_string(val): True
            }, left))
        elif left.name == "tan":
            print("x = " + build_sol({
                "k%s" % pi_s: True,
                "+" if sol > 0 else "-": False,
                "arctan(%s)" % get_num_string(abs(val)): True
            }, left))

def inequ(expr, val, op):
    """求解三角不等式

    @param expr 一个式子
    @param val  值
    @param op   不等号
    """
    try:
        left = trig_eval(expr, True)
        if not is_simplest(left):
            print("ERROR: Only support simplest trigonometric inequation!")
            return
    except:
        print("Error: Invalid left expr!")
        return
    try:
        value = float(trig_eval(val))
    except ValueError:
        print("Error: Invalid right value!")
        return 
    # 根据不等号设置区间开闭
    get_open = lambda: "(" if "=" not in op else "["
    get_close = lambda: ")" if "=" not in op else "]"
    # sin和cos较麻烦，除了最后的print就别想看懂了（尽管有很多注释，但是不借助单位圆绝对无法理解）
    if left.name == "sin":
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
                x1 = [get_num_string(-math.tau + x1[1], True), -math.tau + x1[1]]
            elif value < 0:
                # 此时终小于始，需调整
                x2 = [get_num_string(x2[1] + math.tau, True), x2[1] + math.tau]
        if value == 0:
            print("%s2k%s-%s, 2k%s%s" % ((get_open(), ) + (pi_s, ) * 3) + (get_close(), ))
        else:
            print("%s2k%s%s%s, 2k%s%s%s%s" % (get_open(), pi_s, "+" if x1[1] > 0 else "", x1[0] if x1[1] != 0 else "", pi_s, "+" if x2[1] > 0 else "", x2[0], get_close()))
    elif left.name == "cos":
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
            x2 = [get_num_string(x2[1] + math.tau, True), x2[1] + math.tau]
        elif (">" in op) and (value < 0):
            # 此时解集穿过x轴正半轴
            x1, x2 = x2, x1
            x1 = [get_num_string(-math.tau + x1[1], True), -math.tau + x1[1]]
        if ("<" in op) and (value == 0):
            print("%s2k%s+%s/2, 2k%s+3%s/2%s" % ((get_open(), ) + (pi_s, ) * 4) + (get_close(), ))
        else:
            print("%s2k%s%s%s, 2k%s%s%s%s" % (get_open(), pi_s, "+" if x1[1] >= 0 else "", x1[0], pi_s, "+" if x2[1] > 0 else "", x2[0], get_close()))
    elif left.name == "tan":
        # tan最简单，看函数图像即可出结果
        sol = math.atan(value)
        if ">" in op:
            print("%sk%s%s%s, k%s+%s/2)" % (get_open(), pi_s, "+" if sol >= 0 else "", get_num_string(sol), pi_s, pi_s))
        elif "<" in op:
            print("(k%s+%s/2, k%s%s%s%s" % (pi_s, pi_s, pi_s, "+" if sol >= 0 else "", get_num_string(sol), get_close()))

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

