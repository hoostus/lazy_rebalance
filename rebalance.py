#!/usr/bin/env python

"""
Original JavaScript version: http://optimalrebalancing.tk/index.html
---------- Optimal lazy rebalancing calculator:
Copyright 2013 Albert H. Mao

This program is free software: you can redistribute it and/or modify it under the terms of the
GNU General Public License as published by the Free Software Foundation, either version 3 of the
License, or (at your option) any later version.

This program is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; without
even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU
General Public License for more details.

You should have received a copy of the GNU General Public License along with this program. If
not, see <http://www.gnu.org/licenses/>.
"""

from collections import namedtuple
import operator
from functools import reduce
from pprint import pprint

Asset = namedtuple('Asset', ['name', 'target', 'value'])

ASSETS = [
    Asset('Bond fund', 0.20, 16_500),
    Asset('TIPS fund', 0.10, 6_500),
    Asset('Domestic stock fund', 0.40, 43_500),
    Asset('International stock fund', 0.30, 33_500),
]

def rebalance(amount, assets=ASSETS):
    """

    >>> rebalance(5_000)
    [('TIPS fund', 2833.333333333333), ('Bond fund', 2166.666666666667)]
    >>> rebalance(30_000)
    [('TIPS fund', 6500.0), ('Bond fund', 9500.0), ('Domestic stock fund', 8499.999999999996), ('International stock fund', 5500.000000000001)]
    >>> rebalance(-12_000)
    [('International stock fund', -5642.857142857143), ('Domestic stock fund', -6357.142857142856)]
    >>> rebalance(-35_000)
    [('International stock fund', -13999.999999999998), ('Domestic stock fund', -17500.0), ('Bond fund', -3499.999999999999)]
    """

    def fracdev(a, t):
        return (a/t) - 1

    total = amount + reduce(operator.add, [a.value for a in assets])

    all_f = [(a, fracdev(a.value, a.target*total)) for a in assets]
    all_f = sorted(all_f, key=lambda x: x[1])

    if amount < 0:
        all_f = list(reversed(all_f))

    h = 0 # accumulator of some kind?
    k = 0 # some factor thing
    e = 0 # keeps track of when we ran out of money
    for i, (a, f) in enumerate(all_f):
        if not abs(amount) > 0:
            break

        k = f
        targetValue = total * a.target
        h += targetValue

        if i >= len(all_f) - 1:
            l = 0
        else:
            l = all_f[i+1][1]

        t = h * (l - k)

        # need to use abs() to handle withdrawal cases (i.e. negative amounts)
        if abs(t) <= abs(amount):
            amount -= t
            k = l
        else:
            k = k + (amount/h)
            amount = 0
        e += 1

    actions = []

    for i, (a, f) in enumerate(all_f):
        if i >= e:
            break
        targetValue = total * a.target
        delta = targetValue * (k - f)
        actions.append((a.name, delta))

    return actions

if __name__ == '__main__':
    import doctest
    doctest.testmod()