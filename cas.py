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

"""一个没有任何用处的小型CAS系统

这个CAS系统没有任何作用，它仅仅用于将用户在eval()中输入的字符串解析成适合计算机理解的数据。
"""

from numbers import Number
from fractions import Fraction
from mpmath import fp

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
            return "%s%s" % (a if abs(a) != 1 else str(a).replace("1", ""), chr(960))
        if always_p:
            return "%s%s/%s" % (a if abs(a) != 1 else str(a).replace("1", ""), chr(960), b)
        else:
            if fp.almosteq((a + 1) / b, 2):
                return "-%s/%s" % (chr(960), b)
            else:
                return "%s%s/%s" % (a if abs(a) != 1 else str(a).replace("1", ""), chr(960), b)
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


class Add(object):
    """几个代数式之和"""

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
        elif isinstance(other, (Number, MathItem)):
            self.args.append(other)
        else:
            raise TypeError()
        return self

    def __radd__(self, other):
        if isinstance(other, Number) and isinstance(self.args[-1], Number):
            self.args[-1] += other
        elif isinstance(other, (Number, MathItem)):
            self.args.insert(0, other)
        else:
            raise TypeError()
        return self

    def __sub__(self, other):
        if isinstance(other, Number) and isinstance(self.args[-1], Number):
            self.args[-1] -= other
        if isinstance(other, (Number, MathItem)):
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


class Mul(object):
    """几个代数式之积"""

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
        return Add(self, other)

    def __radd__(self, other):
        return Add(other, self)

    def __sub__(self, other):
        return Add(self, -other)

    def __mul__(self, other):
        if isinstance(other, Number) and isinstance(self.args[0], Number):
            self.args[0] *= other
        elif isinstance(other, Number):
            self.args.insert(0, other)
        elif isinstance(other, (MathItem)):
            self.args.append(other)
        else:
            raise TypeError()
        return self

    def __rmul__(self, other):
        if isinstance(other, Number) and isinstance(self.args[0], Number):
            self.args[0] *= other
        elif isinstance(other, Number):
            self.args.insert(0, other)
        elif isinstance(other, MathItem):
            self.args.append(other)
        else:
            raise TypeError()
        return self

    def __truediv__(self, other):
        if isinstance(other, Number):
            if isinstance(self.args[0], Number):
                self.args[0] /= other
            else:
                self.args.insert(0, 1 / other)
            if fp.almosteq(self.args[0], 1):
                self.args = self.args[1:]
            return self
        raise TypeError()

    def __repr__(self):
        result = []
        for item in self.args:
            if isinstance(item, Number):
                if item > 0:
                    result.append(get_num_string(item, True))
                else:
                    result.append("(%s)" % get_num_string(item, True))
            else:
                if isinstance(item, Add):
                    result.append("(%s)" % repr(item))
                else:
                    result.append(repr(item))
        return "".join(result)


class MathItem(object):

    def __init__(self):
        self.name = ""

    def __eq__(self, other):
        return self.name == other.name

    def __add__(self, other):
        return Add(self, other)

    def __radd__(self, other):
        return Add(other, self)

    def __sub__(self, other):
        return Add(self, -other)

    def __rsub__(self, other):
        return Add(other, -self)

    def __mul__(self, other):
        return Mul(self, other)

    def __rmul__(self, other):
        return Mul(other, self)

    def __truediv__(self, other):
        return Mul(self, 1 / other)

class Function(MathItem):
    """一个函数"""

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
    """一个变量"""

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

pi = Const(chr(960), fp.pi)
e = Const("e", fp.e)
