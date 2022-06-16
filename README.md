# TRIG
TRIG是一个最简三角方程、最简三角不等式求解器。

怎么说呢，有如下优点：

- 它是使用Python标准库写成的，只依赖了`mpmath`（`sympy`是个大家伙，尽量不要去不用）
  > 精确的三角学对计算机来说确实是一个挑战
- 它与学校的教学完全相同
  > 为了满足老师对解集的要求，此程序多次改版

为了实现复杂的功能，内含一个小型的CAS系统。

<details>
<summary>方程、不等式的解法</summary>
<p>

方程嘛，挺简单的。大家都背过公式吧，套公式就可以了。

不等式嘛，利用单位圆或函数图像吧：`sin`横截单位圆；`cos`纵截单位圆；其它的看函数图像。
> 确实挺好实现的呢，代码我自己都看不懂（你不认为这样子可以平添几分神秘性吗）。

</p>
</details>

## 使用
输入`python -m trig`进入TRIG。

要计算方程或不等式，应使用`do`命令：
```
>>> do sin(x)=1/2
x = kπ + (-1)^k * π/6
>>> do cos(x)>sqrt(3)/2
(2kπ-π/6, 2kπ+π/6)
```

若想要获得在某一区间内的解（上述返回的是通解），需要设置定义域（全闭区间）：
```
>>> set D 0 2*pi
>>> do sin(x)=1/2
x = kπ + (-1)^k * π/6
Solution in D: {π/6, 5π/6}
```

若要再次获得某一范围内的解，需重新设置。

### 对输入数字的一些小小的要求
那些以字符串形式输入的数会通过Python的内置函数`eval`运算后转换为浮点数。

为了保证安全，只提供4个函数2个变量，且不能调用内置函数：

- 函数`sin`、`cos`、`tan`：三个三角函数
- 函数`sqrt`： 计算平方根
- 变量`pi`：π
- 变量`x`：某未知数

三角函数和`x`只能在等号左边使用（解方程不等式时）。

## 还会搞什么小玩意？
何不遐想一下，把一些三角学的小玩意搞出来？

## 小小的提示
学术交流，仅仅适用于学术交流！

该程序使用MIT许可证。
