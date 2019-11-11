# -*- coding: utf-8 -*-

# This code is part of Qiskit.
#
# (C) Copyright IBM 2017, 2018.
#
# This code is licensed under the Apache License, Version 2.0. You may
# obtain a copy of this license in the LICENSE.txt file in the root directory
# of this source tree or at http://www.apache.org/licenses/LICENSE-2.0.
#
# Any modifications or derivative works of this code must retain this
# copyright notice, and modified files need to carry a notice indicating
# that they have been altered from the originals.

"""Utility functions for working with Results."""

from functools import reduce
from re import match
from qiskit import QiskitError


def marginal_counts(counts, indices=None, pad_zeros=False):
    """Marginalize counts from an experiment over some indices of interest.

    Args:
        counts (dict): Counts of some measurement results, to be marginalized.
        indices (list(int) or None): The bit positions of interest to NOT marinalize over.
            If None, do not marginalize at all.
        pad_zeros (Bool): Include zero count outcomes in return dict.

    Returns:
        dict[str:int]: a dictionary with the observed counts, marginalized to
            only account for frequency of observations of bits of interest.
    """
    # Extract total number of clbits from first count key
    # We trim the whitespace seperating classical registers
    # and count the number of digits
    num_clbits = len(next(iter(counts)).replace(' ', ''))

    # Check if we do not need to marginalize. In this case we just trim
    # whitespace from count keys
    if (indices is None) or set(range(num_clbits)) == set(indices):
        ret = {}
        for key, val in counts.items():
            key = key.replace(' ', '')
            ret[key] = val
        return ret

    if not set(indices).issubset(set(range(num_clbits))):
        raise QiskitError('indices must be in range [0, {0}].'.format(num_clbits-1))

    # Sort the indices to keep in decending order
    # Since bitstrings have qubit-0 as least significant bit
    indices = sorted(indices, reverse=True)

    # Generate bitstring keys for indices to keep
    meas_keys = count_keys(len(indices))

    # Get regex match strings for suming outcomes of other qubits
    rgx = []
    for key in meas_keys:
        def _helper(x, y):
            if y in indices:
                return key[indices.index(y)] + x
            return '\\d' + x
        rgx.append(reduce(_helper, range(num_clbits), ''))

    # Build the return list
    meas_counts = []
    for m in rgx:
        c = 0
        for key, val in counts.items():
            if match(m, key.replace(' ', '')):
                c += val
        meas_counts.append(c)

    # Return as counts dict on desired indices only
    if pad_zeros is True:
        return dict(zip(meas_keys, meas_counts))
    ret = {}
    for key, val in zip(meas_keys, meas_counts):
        if val != 0:
            ret[key] = val
    return ret


def count_keys(num_clbits):
    """Return ordered count keys."""
    return [bin(j)[2:].zfill(num_clbits) for j in range(2 ** num_clbits)]
