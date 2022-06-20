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

try:
    import mpmath
    from mpmath import fp
except:
    print("Module \"mpmath\" isn't installed, please use `pip install mpmath` to install it!")
    exit()
import re
from fractions import Fraction
from math import gcd
from numbers import Number
if __import__("sys").platform != "win32":
    import readline


class Operator(object):
    pass


class Mul(Operator):

    def __init__(self, *args):
        self.args = list(args)
        prefix, result = 1, []
        for item in args:
            if isinstance(item, Number):
                prefix *= item
            else:
                result.append(item)
        if fp.almosteq(prefix, 1):
            self.args = result
        else:
            self.args = [prefix] + result

    def __mul__(self, other):
        if isinstance(other, Number) and isinstance(self.args[0], Number):
            self.args[0] *= other
        elif isinstance(other, Number):
            self.args.insert(0, other)
        elif isinstance(other, MathItem):
            self.args.append(other)
        else:
            raise TypeError()
        return self

    def __neg__(self):
        if isinstance(self.args[0], Number):
            self.args[0] *= -1
        else:
            self.args.insert(0, -1)
        return self

    def __rmul__(self, other): return self * other


class MathItem(object):

    def __init__(self):
        self.name = ""

    def __eq__(self, other): return isinstance(
        other, self.__class__) and (self.name == other.name)

    def __add__(self, other): return Add(self, other)
    def __radd__(self, other): return Add(other, self)
    def __sub__(self, other): return Add(self, -other)
    def __rsub__(self, other): return Add(other, -self)
    def __mul__(self, other): return Mul(self, other)
    def __rmul__(self, other): return Mul(other, self)
    def __truediv__(self, other): return Mul(self, 1 / other)
    def __neg__(self): return Mul(-1, self)


class Function(MathItem):

    def __init__(self, *args):
        super().__init__()
        self.name = "func"
        self.args = list(args)


class Variable(MathItem):

    def __init__(self, name="x"):
        super().__init__()
        self.name = name


class sin(Function):

    def __init__(self, x):
        super().__init__(x)
        self.name = "sin"


class cos(Function):

    def __init__(self, x):
        super().__init__(x)
        self.name = "cos"


class tan(Function):

    def __init__(self, x):
        super().__init__(x)
        self.name = "tan"


class Triangle():

    def __init__(self, **kwargs):
        self.args = {}
        for i in ["a", "b", "c", "A", "B", "c", "area", "cric"]:
            if kwargs.get(i) is None:
                self.args[i] = None
            else:
                self.args[i] = kwargs[i]

    def get_known_side(self):
        return [side for side in self.args.keys() if (side in ["a", "b", "c"] and self.args[side] is not None)]

    def get_known_angle(self):
        return [side for side in self.args.keys() if (side in ["A", "B", "C"] and self.args[side] is not None)]

    def get_unknown_side(self):
        return [side for side in self.args.keys() if (side in ["a", "b", "c"] and self.args[side] is None)]

    def get_unknown_angle(self):
        return [side for side in self.args.keys() if (side in ["A", "B", "C"] and self.args[side] is None)]

    def can_use_heron_formular(self, which):
        return (which == "area") and (len(self.get_unknown_side()) == 0)

    def heron_formular(self):
        p = (self.args["a"] + self.args["b"] + self.args["c"]) / 2
        a, b, c = self.args["a"], self.args["b"], self.args["c"]
        return fp.sqrt(p * (p - a) * (p - b) * (p - c))

    def can_use_Bb_sin(self, cond):
        for c in "abc":
            if (c in self.args) and (c.upper() in self.args):
                try:
                    result = eval(
                        cond, {"a": 0, "b": 0, "c": 0, "__builtins__": None})
                    if isinstance(result, (int, float)):
                        return True
                except:
                    return False
        return False

    def Bb_sin(self, which):
        known_side = self.get_known_side()[0]
        double_R = self.args[known_side] / \
            fp.sin(self.args[known_side.upper()])
        start, offset, coeff = 0, 0, {}
        d = {"a": which.find("*a"), "b": which.find("*b"), "c": which.find("*c")}
        for symbol, index in d.items():
            if index != -1:
                coeff[symbol] = eval(which[start: index])
                start = index + 2
        if known_side in coeff:
            offset = coeff[known_side] * self.args[known_side]
            del coeff[known_side]
        if len(coeff) == 1:
            return mpmath.iv.sin([0, fp.pi - self.args[known_side.upper()]]) * double_R * list(coeff.values())[0] + offset
        elif len(coeff) == 2:
            a, b = coeff[self.get_unknown_side()[0]] * \
                double_R, coeff[self.get_unknown_side()[1]] * double_R
            phi = self.args[known_side.upper()]
            A, phi = mpmath.polar(
                (a * mpmath.cos(phi) + b) + (a * mpmath.sin(phi)) * 1j)
            return mpmath.iv.sin(mpmath.iv.mpf([0, fp.pi - self.args[known_side.upper()]]) + phi) * A + offset

    def solve(self, which):
        if self.can_use_heron_formular(which):
            return self.heron_formular()
        elif self.can_use_Bb_sin(which):
            return self.Bb_sin(which)


# 定义域，通过set_var函数修改
D = None
# 特殊字符
ang_s = chr(8736)
pi_s = chr(960)
# 特殊的三角方程的解集
special = {
    "sin": {
        -1: {"2*k%s" % pi_s: True, "-": False, fp.pi / 2: True},
        0: {"k" + pi_s: True},
        1: {"2*k%s" % pi_s: True, "+": False, fp.pi / 2: True}
    },
    "cos": {
        -1: {"2*k%s" % pi_s: True, "+": False, fp.pi: True},
        0: {"k%s" % pi_s: True, "+": False, fp.pi / 2: True},
        1: {"2*k" + pi_s: True}
    },
    "tan": {
        0: {"k" + pi_s: True}
    }
}
# 单位圆的弧度圈，逆时针方向，从-pi/2开始
# 为什么是-pi/2而非0呢？很简单，cos(x)>a需要纵截单位圆，这样便于程序设计，且也便于sin(x)>a的运算（横截的话左右对称）
unit_circle = [
    -fp.pi / 2,
    -fp.pi / 3,
    -fp.pi / 4,
    -fp.pi / 6,
    0,
    fp.pi / 6,
    fp.pi / 4,
    fp.pi / 3,
    fp.pi / 2,
    2 * fp.pi / 3,
    3 * fp.pi / 4,
    5 * fp.pi / 6,
    fp.pi,
    7 * fp.pi / 6,
    5 * fp.pi / 4,
    4 * fp.pi / 3
]


def simplify_sqrt(value):
    """化简根式。"""
    i, result = 2, []
    while True:
        if value == i:
            result.append(i)
            break
        if gcd(value, i) == i:
            result.append(i)
            value = value // i
            i = 2
            continue
        i += 1
    inner, outter = [], 1
    for i in result:
        if inner.count(i) == 1:
            inner.remove(i)
            outter *= i
        else:
            inner.append(i)
    return "%ssqrt(%d)" % ("" if outter == 1 else outter, fp.fprod(inner))


def get_num_string(value, always_p=False):
    """返回一些有理数/无理数的分式表示

    1. 弧度
    2. 分数
    3. sqrt(a)/b型的数

    @param value    某浮点数
    @param always_p 返回的弧度是否为正（在弧度值本身为正的情况下），若为True则返回5pi/3而非-pi/3
    """
    if fp.almosteq(value, 0):
        return "0"
    frac = Fraction(value / fp.pi).limit_denominator(10000)
    a, b = frac.as_integer_ratio()
    if fp.almosteq(value, frac * fp.pi):
        if b == 1:
            return "%s%s" % (a if abs(a) != 1 else str(a).replace("1", ""), pi_s)
        if always_p:
            return "%s%s/%s" % (a if abs(a) != 1 else str(a).replace("1", ""), pi_s, b)
        else:
            if fp.almosteq((a + 1) / b, 2):
                return "-%s/%s" % (pi_s, b)
            else:
                return "%s%s/%s" % (a if abs(a) != 1 else str(a).replace("1", ""), pi_s, b)
    else:
        a, b = Fraction(value).limit_denominator(10000).as_integer_ratio()
        if fp.almosteq(value, a / b):
            return "%s%s%s" % (a, "/" if b != 1 else "", "" if b == 1 else b)
        else:
            flag = "" if value > 0 else "-"
            a, b = Fraction(
                value ** 2).limit_denominator(10000).as_integer_ratio()
            if fp.almosteq(value ** 2, a / b, 1e-10):
                if (a == 1) and (b != 1):
                    return "%ssqrt(%s)/%s" % (flag, b, b)
                else:
                    return "%s%s%s%s" % (flag, simplify_sqrt(a), "/" if b != 1 else "", "" if b == 1 else int(fp.sqrt(b)))
            else:
                return str(value)


def get_trig(name, value):
    """返回一个三角比的值对应的弧度（一般情况下是两个）

    @param name  三角比的名称（"s", "c", "t"）
    @param value 三角比的值
    """
    if name[0] == "s":
        f = fp.sin
    if name[0] == "c":
        f = fp.cos
    if name[0] == "t":
        f = fp.tan
    result = []
    for i in unit_circle:
        if fp.almosteq(value, f(i)):
            result.append([get_num_string(i), i])
    return result


def trig_eval(s, cond="num"):
    """解析输入的表达式

    @param s    某表达式
    @param cond 何种类型
    """
    if cond == "trig":
        if s == "s":
            return sin(Variable())
        elif s == "c":
            return cos(Variable())
        elif s == "t":
            return tan(Variable())
        s = s.replace("x", "x()")
        return eval(s, {"cos": lambda x: cos(x), "sin": lambda x: sin(x),
                        "sqrt": fp.sqrt, "pi": fp.pi, "tan": lambda x: tan(x),
                        "x": lambda: Variable("x"), "__builtins__": {}})
    elif cond == "num":
        return eval(s, {"sqrt": fp.sqrt, "pi": fp.pi, "__builtins__": {}})
    elif cond == "ang":
        return eval(s, {"asin": lambda x: fp.asin(x), "acos": lambda x: fp.acos(x),
                        "atan": lambda x: fp.atan(x), "pi": fp.pi, "__builtins__": {}})


def get_coeff_and_addend(left):
    coeff, addend = 1, 0
    if isinstance(left.args[0], Mul):
        coeff = left.args[0].args[0] if isinstance(
            left.args[0].args[0], Number) else 1
    return coeff


def build_sol(expr, left):
    """根据左值和最简方程的解构建最终解

    @param expr 包含解的字典
    @param left 左值
    """
    x_coeff = get_coeff_and_addend(left)
    result = []
    for item, action in expr.items():
        if action == False:
            result.append(item)
        else:
            if isinstance(item, Number):
                result.append(get_num_string(item / x_coeff))
            else:
                if "*" in item:
                    coeff, item = item.split("*")
                else:
                    coeff = 1
                a, b = Fraction(
                    float(coeff) / x_coeff).limit_denominator(1000).as_integer_ratio()
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
        left = trig_eval(expr, "trig")
        if not is_simplest(left):
            print("ERROR: Only support simplest trigonometric equation!")
            return
    except:
        print("Error: Invalid left expr!")
        return
    if left.name == "sin":
        f = fp.asin
    elif left.name == "cos":
        f = fp.acos
    elif left.name == "tan":
        f = fp.atan
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
                if fp.almosteq(k, val):
                    print("x = %s" % build_sol(v, left))
                    return
    if get_num_string(sol).find(pi_s) != -1:
        # 可使用弧度表示的解集
        coeff = get_coeff_and_addend(left)
        if left.name == "sin":
            formula = ["(k * fp.pi + (-1) ** k * %s) %s" %
                       (sol, ("/ (%s)" % coeff) if coeff != 1 else "")]
            print("x = " + build_sol({
                "k%s" % pi_s: True,
                "+" if sol > 0 else "-": False,
                "(-1)**k": False,
                "*": False,
                abs(sol): True
            }, left))
        elif left.name == "cos":
            formula = ["(2 * k * fp.pi + %s) %s" % (sol, ("/ (%s)" % coeff) if coeff != 1 else ""),
                       "(2 * k * fp.pi - %s) %s" % (sol, ("/ (%s)" % coeff) if coeff != 1 else "")]
            print("x = " + build_sol({
                "2*k%s" % pi_s: True,
                chr(177): False,
                sol: True,
            }, left))
        elif left.name == "tan":
            formula = ["(k * fp.pi + %s) %s" %
                       (sol, ("/ (%s)" % coeff) if coeff != 1 else "")]
            print("x = " + build_sol({
                "k%s" % pi_s: True,
                "+" if sol > 0 else "-": False,
                abs(sol): True,
            }, left))
        # 如若设置了定义域，那么就在定义域内找解
        if D is not None:
            first, last, result = 0, 0, []
            try:
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
                            if flag == -1:
                                break
                            i, flag = 1, -1
            except KeyboardInterrupt:
                print("You stop to find solution")
                return
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
        left = trig_eval(expr, "trig")
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
    def get_open(): return "(" if "=" not in op else "["
    def get_close(): return ")" if "=" not in op else "]"
    # sin和cos较麻烦，除了最后的print就别想看懂了（尽管有很多注释，但是不借助单位圆绝对无法理解）
    if left.name == "sin":
        try:
            x1, x2 = get_trig("s", value)
        except:
            print("Error: Could not find solution!")
            return
        if ("<" in op):
            # 解集是逆时针找出的，需对调始终边
            x1, x2 = x2, x1
            if value > 0:
                # 此时解集穿过x轴正半轴，需表示成(2kπ-α, 2kπ+β)
                x1 = [get_num_string(-2 * fp.pi + x1[1],
                                     True), -2 * fp.pi + x1[1]]
            elif value < 0:
                # 此时终小于始，需调整
                x2 = [get_num_string(x2[1] + 2 * fp.pi, True),
                      x2[1] + 2 * fp.pi]
        if value == 0:
            print("%s2k%s-%s, 2k%s%s" %
                  ((get_open(), ) + (pi_s, ) * 3 + (get_close(), )))
        else:
            print("%s2k%s%s%s, 2k%s%s%s%s" % (get_open(
            ), pi_s, "+" if x1[1] > 0 else "", x1[0] if x1[1] != 0 else "", pi_s, "+" if x2[1] > 0 else "", x2[0], get_close()))
    elif left.name == "cos":
        try:
            x1, x2 = get_trig("c", value)
        except:
            print("Error: Could not find solution!")
            return
        if ("<" in op) and (value > 0):
            # 此时解集为第一象限始边到第四象限终边，但由于上述单位圆特性，需对调始终边
            x1, x2 = x2, x1
            x2 = [get_num_string(x2[1] + 2 * fp.pi, True), x2[1] + 2 * fp.pi]
        elif (">" in op) and (value < 0):
            # 此时解集穿过x轴正半轴
            x1, x2 = x2, x1
            x1 = [get_num_string(-2 * fp.pi + x1[1], True), -2 * fp.pi + x1[1]]
        if ("<" in op) and (value == 0):
            print("%s2k%s+%s/2, 2k%s+3%s/2%s" %
                  ((get_open(), ) + (pi_s, ) * 4 + (get_close(), )))
        else:
            print("%s2k%s%s%s, 2k%s%s%s%s" % (get_open(
            ), pi_s, "+" if x1[1] >= 0 else "", x1[0], pi_s, "+" if x2[1] > 0 else "", x2[0], get_close()))
    elif left.name == "tan":
        # tan最简单，看函数图像即可出结果
        sol = fp.atan(value)
        if ">" in op:
            print("%sk%s%s%s, k%s+%s/2)" % (get_open(), pi_s,
                  "+" if sol >= 0 else "", get_num_string(sol), pi_s, pi_s))
        elif "<" in op:
            print("(k%s+%s/2, k%s%s%s%s" % (pi_s, pi_s, pi_s,
                  "+" if sol >= 0 else "", get_num_string(sol), get_close()))


def sol_trig(*args):
    """解三角形。"""
    kwargs = {}
    which = False
    for arg in args:
        if which == True:
            which = arg
            break
        if arg == "get":
            which = True
            continue
        k, v = arg.split("=")
        try:
            if k in ["a", "b", "c", "area", "cric"]:
                kwargs[k] = trig_eval(v)
            elif k in ["A", "B", "C"]:
                kwargs[k] = trig_eval(v, "ang")
        except:
            print("Error: Bad argument: \"%s\"!" % arg)
            return
    if isinstance(which, bool):
        print("Error: A unknow value must given!")
        return
    trig = Triangle(**kwargs)
    solution = trig.solve(which)
    if isinstance(solution, mpmath.ctx_iv.ivmpf):
        a, b = get_num_string(
            float(solution.a)), get_num_string(float(solution.b))
        print("(%s, %s)" % (a, b))
    elif solution is None:
        print("This triangle is unsolvable!")
    else:
        print(get_num_string(float(solution)))


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
            elif action == "trig":
                sol_trig(*args.split(" "))
