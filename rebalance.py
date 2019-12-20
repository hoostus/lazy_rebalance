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

__test_assets__ = [('Bond fund', 0.20, 16_500),
    ('TIPS fund', 0.10, 6_500),
    ('Domestic stock fund', 0.40, 43_500),
    ('International stock fund', 0.30, 33_500)]

def fracdev(a, t):
    return (a/t) - 1

Asset = namedtuple('Asset', ['name', 'targetValue', 'value', 'deviation'])

def make_tuple(totalValue, assets):
    """ Given an list of (name, percentage, value) create the named tuples """
    def mk(name, pct, value):
        targetValue = totalValue * pct
        dev = fracdev(value, targetValue)
        return Asset(name, targetValue, value, dev)

    return [mk(*a) for a in assets]

def get_next_deviation(assets):
    # If there are no other assets in the list then the 'next level' is
    # "no deviations at all", so return 0
    if not assets:
        return 0
    else:
        return assets[0].deviation

def calc_assets(amount, rest, assets):
    a = rest.pop(0)
    # the distance to the next deviation level
    catch_up = get_next_deviation(rest) - a.deviation
    # we need to calculate how much it would cost to reach the next deviation
    # level not just for ourselves, but also for everyone else before us,
    # who are also now at our deviation level.
    sum_targetValues = reduce(operator.add, [n.targetValue for n in assets], a.targetValue)
    delta = catch_up * sum_targetValues
    # We need the absolute value because we don't know whether we are adding or
    # or removing money to the portfolio; the abs() handles both cases
    if abs(delta) < abs(amount):
        return calc_assets(amount - delta, rest, assets + [a])
    else:
        # When we don't have enough money to *fully* equalize the current asset
        # deviation so the next asset deviation we terminate the loop.
        return assets + [a]

# This is unfortunately similar to above loop construct. Except this time
# We want to calculate, given the amount of money we have, how much we can
# correct the deviation of the *last* set of assets.
def calc_deviation_for_money(amount, rest, sum_targetValues):
    a = rest.pop(0)
    sum_targetValues += a.targetValue
    catch_up = get_next_deviation(rest) - a.deviation
    delta = catch_up * sum_targetValues
    if abs(delta) < abs(amount):
        return calc_deviation_for_money(amount - delta, rest, sum_targetValues)
    else:
        # given the amount of money we have left after catching everyone below
        # us up to *us*, how far can we move our *own* deviation? Keeping in
        # mind that we need to bring along with us, everyone who is now equal
        # to us. That's why we have the sum_targetValues here.
        return amount / sum_targetValues

def rebalance(amount, assets):
    """
    >>> rebalance(5_000, __test_assets__)
    [('TIPS fund', 2833.333333333333), ('Bond fund', 2166.666666666667)]
    >>> rebalance(30_000, __test_assets__)
    [('TIPS fund', 6500.0), ('Bond fund', 9500.0), ('Domestic stock fund', 8499.999999999996), ('International stock fund', 5500.000000000001)]
    >>> rebalance(-12_000, __test_assets__)
    [('International stock fund', -5642.857142857143), ('Domestic stock fund', -6357.142857142856)]
    >>> rebalance(-35_000, __test_assets__)
    [('International stock fund', -13999.999999999998), ('Domestic stock fund', -17500.0), ('Bond fund', -3499.999999999999)]
    """

    def get_value(n):
        return n[2]

    total = reduce(operator.add, [get_value(a) for a in assets], amount)

    # This will also calculate the error ('deviation') from the targetValue for each
    all_assets = make_tuple(total, assets)

    # Sort them in the order we want to reduce the errors.
    # A positive *amount* means we want to reduce the most underweight things
    # first (by adding to them)
    all_assets = list(sorted(all_assets, key=lambda x: x.deviation))

    # A negative *amount* means we want to reduce the most overweight things
    # first (by removing from them)
    if amount < 0:
        all_assets = list(reversed(all_assets))

    # Next we generate a list of all the assets we have enough money to reduce
    # deviation for.
    affected_assets = calc_assets(amount, all_assets.copy(), [])

    # Calculate the final target deviation we want all of the above assets to reach
    # given the amount of money we have on hand.
    target_deviation = affected_assets[-1].deviation
    target_deviation += calc_deviation_for_money(amount, affected_assets.copy(), 0)

    # Given that target deviation, calculate the actual dollar amounts we need to move
    return [(a.name, a.targetValue * (target_deviation - a.deviation)) for a in affected_assets]

if __name__ == '__main__':
    import doctest
    doctest.testmod()