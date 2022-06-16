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
    from mpmath import fp
except:
    print("'mpmath' isn't installed, use `pip install mpmath` to install it!")
    exit()
from numbers import Number
from fractions import Fraction
if __import__("sys").platform != "win32":
    import readline

# 定义域，通过set_var函数修改
D = None
# 表示圆周率的字符
pi_s = chr(960)
# 特殊的三角方程的解集
special = {
    "sin": {
        -1: {"2*k%s" % pi_s: True, "-": False,fp.pi / 2: True},
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


class Operator(object):
    pass


class Add(Operator):

    def __init__(self, *args):
        prefix, result = 0, []
        for item in args:
            if isinstance(item, Number):
                prefix += item
            else:
                result.append(item)
        if prefix != 0:
            self.args = result + [prefix]
        else:
            self.args = result

    def __add__(self, other):
        if isinstance(other, Number) and isinstance(self.args[-1], Number):
            self.args[-1] += other
        elif isinstance(other, (Number, MathItem, Operator)):
            if isinstance(other, Mul) and isinstance(self.args[-1], Mul) and (len(self.args[-1].args) == 2) and \
                    isinstance(self.args[-1].args[0], Number) and (self.args[-1].args[-1] == pi):
                if (len(other.args) == 2) and isinstance(other.args[0], Number) and (other.args[-1] == pi):
                    self.args[-1] += other
            else:
                self.args.append(other)
        else:
            raise TypeError()
        return self

    def __radd__(self, other): return other + self

    def __sub__(self, other):
        if isinstance(other, Number) and isinstance(self.args[-1], Number):
            self.args[-1] -= other
        if isinstance(other, (Number, MathItem, Operator)): 
            self.args.append(-other)
        else:
            raise TypeError()
        return self

    def __truediv__(self, other):
        if isinstance(other, Number):
            result = []
            for item in self.args:
                result.append(item / other)
            self.args = result
            return self
        raise TypeError()

    def __repr__(self):
        first, result = True, []
        for item in self.args:
            if isinstance(item, Number):
                if item >= 0:
                    result.append(("+" if not first else "") + get_num_string(item, True))
                else:
                    result.append(get_num_string(item))
            else:
                result.append(("+" if not first else "") + repr(item))
            first = False
        return "".join(result)


class Mul(Operator):

    def __init__(self, *args):
        self.args = list(args)
        prefix, result = 1, []
        for item in args:
            if isinstance(item, Number):
                prefix *= item
            else:
                result.append(item)
        self.args = [prefix] + result

    def __add__(self, other):
        if isinstance(other, Mul) and (len(self.args) == 2) and isinstance(self.args[0], Number) and (self.args[-1] == pi):
                if (len(other.args) == 2) and isinstance(other.args[0], Number) and (other.args[-1] == pi):
                    return Mul(self.args[0] + other.args[0], pi)
        return Add(self, other)

    def __mul__(self, other):
        if isinstance(other, Number) and isinstance(self.args[0], Number):
            self.args[0] *= other
        elif isinstance(other, Number):
            self.args.insert(0, other)
        elif isinstance(other, (MathItem, Operator)):
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

    def __radd__(self, other): return other + self
    def __sub__(self, other): return self + (-other)
    def __rmul__(self, other): return self * other
    def __truediv__(self, other): return Div(self, other)

    def __repr__(self):
        result = []
        for item in self.args:
            if isinstance(item, Number):
                result.append(get_num_string(item, True))
            else:
                if isinstance(item, (Add, Div)):
                    result.append("(%s)" % repr(item))
                else:
                    result.append(repr(item))
        return "".join(result)


class Div(Operator):

    def __init__(self, a, b):
        assert isinstance(b, Number)
        self.args = [a, b]

    def __add__(self, other):
        if isinstance(other, Div) and fp.almosteq(self.args[1], other.args[1]):
            return Div(self.args[0] + other.args[0], self.args[1])

    def __truediv__(self, other):
        assert isinstance(other, Number)

    def __repr__(self):
        if ("/" in get_num_string(self.args[1])) and (pi_s not in get_num_string(self.args[1])):
            a, b = map(int, get_num_string(self.args[1]).split("/"))
            if isinstance(self.args[0], Mul) and (len(self.args[0].args) == 2) \
                    and (isinstance(self.args[0].args[0], Number)):
                a *= self.args[0].args[0]
                return "%s%s/%s" % (a, self.args[0].args[1], b)
            return "%s(%s)/%s" % (a, repr(self.args[0]), b)
        else:
            if isinstance(self.args[0], Operator) and (not isinstance(self.args[0], Mul)):
                return "(%s)/%s" % (repr(self.args[0]), self.args[1])
            return "%s/%s" % (repr(self.args[0]), self.args[1])


class MathItem(object):

    def __init__(self):
        self.name = ""

    def __eq__(self, other): return isinstance(other, self.__class__) and (self.name == other.name)
    def __add__(self, other): return Add(self, other)
    def __radd__(self, other): return Add(other, self)
    def __sub__(self, other): return Add(self, -other)
    def __rsub__(self, other): return Add(other, -self)
    def __mul__(self, other): return Mul(self, other)
    def __rmul__(self, other): return Mul(other, self)
    def __truediv__(self, other): return Div(self, other)

class Function(MathItem):

    def __init__(self, *args):
        super().__init__()
        self.name = "func"
        self.args = args
 
    def __repr__(self):
        args = []
        for item in self.args:
            if isinstance(item, Number):
                args.append(get_num_string(item, True))
            else:
                args.append(repr(item))
        args = ",".join(args)
        return "%s(%s)" % (self.name, args)


class Variable(MathItem):

    def __init__(self, name="x"):
        super().__init__()
        self.name = name

    def __repr__(self):
        return "%s" % self.name


class Const(Variable):

    def __init__(self, name, value):
        super().__init__()
        self.name = name
        self.value = value

    def __float__(self):
        return float(self.value)


pi = Const(pi_s, fp.pi)


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


def get_num_string(value, always_p=False):
    """返回一些有理数/无理数的分式表示

    1. 弧度
    2. 分数
    3. sqrt(a)/b型的数

    @param value    某浮点数
    @param always_p 返回的弧度是否为正（在弧度值本身为正的情况下），若为True则返回5pi/3而非-pi/3
    """
    if fp.almosteq(value, 0): return "0"
    frac = Fraction(value / fp.pi).limit_denominator(1000)
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
        a, b = Fraction(value).limit_denominator(1000).as_integer_ratio()
        if fp.almosteq(value, a / b):
            return "%s%s%s" % (a, "/" if b != 1 else "", "" if b == 1 else b)
        else:
            flag = "" if value > 0 else "-"
            a, b = Fraction(value ** 2).limit_denominator(1000).as_integer_ratio()
            if fp.almosteq(value ** 2, a / b):
                return "%ssqrt(%s)%s%s" % (flag, a, "/" if b != 1 else "", "" if b == 1 else int(fp.sqrt(b)))
            else:
                return str(value)

def get_trig(name, value):
    """返回一个三角比的值对应的弧度（一般情况下是两个）

    @param name  三角比的名称（"s", "c", "t"）
    @param value 三角比的值
    """
    if name[0] == "s": f = fp.sin
    if name[0] == "c": f = fp.cos
    if name[0] == "t": f = fp.tan
    result = []
    for i in unit_circle:
        if fp.almosteq(value, f(i)):
            result.append([get_num_string(i), i])
    return result

def trig_eval(s, left=False):
    """解析输入的表达式

    @param s    某表达式
    @param left 是否为等号左边的表达式
    """
    if left:
        if s == "s": return sin(Variable())
        elif s == "c": return cos(Variable())
        elif s == "t": return tan(Variable())
        s = s.replace("x", "x()")
        return eval(s, {"cos": lambda x: cos(x), "sin": lambda x: sin(x),
            "sqrt": fp.sqrt, "pi": fp.pi, "tan": lambda x: tan(x),
            "x": lambda: Variable("x"), "__builtins__": {}})
    else:
        return eval(s, {"sqrt": fp.sqrt, "pi": fp.pi, "__builtins__": {}})

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
            if isinstance(item, (Number, fp.mpf)):
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
    if left.name == "sin": f = fp.asin
    elif left.name == "cos": f = fp.acos
    elif left.name == "tan": f = fp.atan
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
        coeff = left.args[0].args[0] if isinstance(left.args[0], Mul) else 1
        if left.name == "sin":
            formula = ["(k * fp.pi + (-1) ** k * %s) %s" % (sol, ("/ (%s)" % coeff) if coeff != 1 else "")]
            print("x = " + build_sol({
                "k%s" % pi_s: True,
                "+" if sol > 0 else "-": False,
                "(-1)**k": False,
                "*": False,
                abs(sol): True
            }, left))
        elif left.name == "cos":
            formula = ["(2 * k * fp.pi + %s) %s" % (sol, ("/ (%s)" % coeff) if coeff != 1 else ""),
                    "(2 * k * math.pi - %s) %s" % (sol, ("/ (%s)" % coeff) if left.coeff != 1 else "")]
            print("x = " + build_sol({
                "2*k%s" % pi_s: True,
                chr(177): False,
                sol: True,
            }, left))
        elif left.name == "tan":
            formula = ["(k * fp.pi + %s) %s" % (sol, ("/ (%s)" % coeff) if coeff != 1 else "")]
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
        try:
            x1, x2 = get_trig("s", value)
        except:
            print("Error: Could not find solution!")
            return
        if ("<" in op):
            # 解集是逆时针找出的，需对调始终边
            x1, x2 = x2, x1
            if value > 0:
                # 此时解集穿过x轴正半轴，需表示成(2*k*pi-a, 2*k*pi+b)
                x1 = [get_num_string(-2 * fp.pi + x1[1], True), -2 * fp.pi + x1[1]]
            elif value < 0:
                # 此时终小于始，需调整
                x2 = [get_num_string(x2[1] + 2 * fp.pi, True), x2[1] + 2 * fp.pi]
        if value == 0:
            print("%s2k%s-%s, 2k%s%s" % ((get_open(), ) + (pi_s, ) * 3 + (get_close(), )))
        else:
            print("%s2k%s%s%s, 2k%s%s%s%s" % (get_open(), pi_s, "+" if x1[1] > 0 else "", x1[0] if x1[1] != 0 else "", pi_s, "+" if x2[1] > 0 else "", x2[0], get_close()))
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
            print("%s2k%s+%s/2, 2k%s+3%s/2%s" % ((get_open(), ) + (pi_s, ) * 4 + (get_close(), )))
        else:
            print("%s2k%s%s%s, 2k%s%s%s%s" % (get_open(), pi_s, "+" if x1[1] >= 0 else "", x1[0], pi_s, "+" if x2[1] > 0 else "", x2[0], get_close()))
    elif left.name == "tan":
        # tan最简单，看函数图像即可出结果
        sol = fp.atan(value)
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

