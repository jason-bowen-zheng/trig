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

"""一个没有任何用处的小型CAS系统"""

from fractions import Fraction
import math

def get_num_string(value, always_p=False):
    """返回一些有理数/无理数的分式表示

    1. 弧度（a*pi/b）
    2. 分数（小数位数小于四位）
    3. sqrt(a)/b型的数（平方后小数位数小于四位）

    @param value    某浮点数
    @param always_p 返回的弧度是否为正，若为True则返回5pi/3而非-pi/3
    """
    if value == 0: return "0"
    frac = Fraction(value / math.pi).limit_denominator(1000)
    a, b = frac.as_integer_ratio()
    if math.isclose(value, frac * math.pi):
        if b == 1:
            return "%s%s" % (a if abs(a) != 1 else str(a).replace("1", ""), chr(960))
        if always_p:
            return "%s%s/%s" % (a if abs(a) != 1 else str(a).replace("1", ""), chr(960), b)
        else:
            if math.isclose((a + 1) / b, 2):
                return "-%s/%s" % (chr(960), b)
            else:
                return "%s%s/%s" % (a if abs(a) != 1 else str(a).replace("1", ""), chr(960), b)
    else:
        a, b = Fraction(value).limit_denominator(1000).as_integer_ratio()
        if math.isclose(value, a / b):
            return "%s%s%s" % (a, "/" if b != 1 else "", "" if b == 1 else b)
        else:
            flag = "" if value > 0 else "-"
            a, b = Fraction(value ** 2).limit_denominator(1000).as_integer_ratio()
            print(a, b)
            if math.isclose(value ** 2, a / b):
                return "%ssqrt(%s)%s%s" % (flag, a, "/" if b != 1 else "", "" if b == 1 else math.isqrt(b))
            else:
                return str(value)


class Add(object):
    """几个代数式之和"""

    def __init__(self, *args):
        self.args = list(args)

    def __add__(self, other):
        if isinstance(other, (int, float)) and isinstance(self.args[-1], (int, float)):
            self.args[-1] += other
        elif isinstance(other, (int, float, Function, Variable)):
            self.args.append(other)
            return self
        raise TypeError()

    def __radd__(self, other):
        if isinstance(other, (int, float)) and isinstance(self.args[-1], (int, float)):
            self.args[-1] += other
        elif isinstance(other, (int, float, Function, Variable)):
            self.args.insert(0, other)
            return self
        raise TypeError()

    def __sub__(self, other):
        if isinstance(other, (int, float)) and isinstance(self.args[-1], (int, float)):
            self.args[-1] -= other
        if isinstance(other, (int, float, Function, Variable)):
            self.args.append(-other)
        else:
            raise TypeError()
        return self

    def __repr__(self):
        first, result = True, []
        for item in self.args:
            if isinstance(item, (int, float)):
                if item >= 0:
                    result.append(("+" if not first else "") + get_num_string(item, True))
                else:
                    result.append(get_num_string(item))
            else:
                if item.coeff > 0:
                    result.append(("+" if not first else "") + repr(item))
                else:
                    result.append(get_num_string(item, True))
            first = False
        return "".join(result)


class Function(object):
    """一个函数"""

    def __init__(self, *args):
        self.name = "func"
        self.args = args
        self.coeff = 1

    def __add__(self, other):
        return Add(self, other)

    def __radd__(self, other):
        return Add(other, self)

    def __sub__(self, other):
        return Add(self, -other)

    def __rsub__(self, other):
        return Add(other, -self)

    def __mul__(self, other):
        if isinstance(other, (int, float)):
            self.coeff *= other
            return self
        else:
            raise TypeError()

    def __rmul__(self, other):
        if isinstance(other, (int, float)):
            self.coeff *= other
            return self
        else:
            raise TypeError()

    def __repr__(self):
        args = []
        for item in self.args:
            if isinstance(item, (int, float)):
                args.append(get_num_string(item, True))
            else:
                args.append(repr(item))
        args = ",".join(args)
        return "%s%s(%s)" % (get_num_string(self.coeff, True) if abs(self.coeff) != 1 else str(self.coeff).replace("1", ""),
                self.name, args)


class Variable(object):
    """一个变量"""

    def __init__(self):
        self.name = "x"
        self.coeff = 1

    def __add__(self, other):
        return Add(self, other)

    def __radd__(self, other):
        return Add(other, self)

    def __sub__(self, other):
        return Add(self, -other)

    def __rsub__(self, other):
        return Add(other, -self)

    def __mul__(self, other):
        if isinstance(other, (int, float)):
            self.coeff *= other
            return self
        else:
            raise TypeError()

    def __rmul__(self, other):
        if isinstance(other, (int, float)):
            self.coeff *= other
            return self
        else:
            raise TypeError()

    def __repr__(self):
        return "%s%s" % (get_num_string(self.coeff, True) if abs(self.coeff) != 1 else str(self.coeff).replace("1", ""),
                self.name)


class Sine(Function):

    def __init__(self, x):
        super().__init__(x)
        self.name = "sin"


class Cosine(Function):

    def __init__(self, x):
        super().__init__(x)
        self.name = "cos"


class Tangent(Function):

    def __init__(self, x):
        super().__init__(x)
        self.name = "tan"

