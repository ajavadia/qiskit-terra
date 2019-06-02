# -*- coding: utf-8 -*-

# This code is part of Qiskit.
#
# (C) Copyright IBM 2017, 2019.
#
# This code is licensed under the Apache License, Version 2.0. You may
# obtain a copy of this license in the LICENSE.txt file in the root directory
# of this source tree or at http://www.apache.org/licenses/LICENSE-2.0.
#
# Any modifications or derivative works of this code must retain this
# copyright notice, and modified files need to carry a notice indicating
# that they have been altered from the originals.


"""Test random circuit generation utility."""

from qiskit.circuit import QuantumCircuit
from qiskit.circuit import Measure
from qiskit.circuit.random import random_circuit
from qiskit.converters import circuit_to_dag
from qiskit.test import QiskitTestCase


class TestCircuitRandom(QiskitTestCase):
    """Testing qiskit.circuit.random"""

    def test_simple_random(self):
        """Test creating a simple random circuit.
        """
        circ = random_circuit(width=5, depth=4)
        self.assertIsInstance(circ, QuantumCircuit)
        self.assertEqual(circ.width(), 5)
        self.assertEqual(circ.depth(), 4)

    def test_random_depth_0(self):
        """Test random depth 0 circuit.
        """
        circ = random_circuit(width=1, depth=0)
        self.assertEqual(circ.width(), 1)
        self.assertEqual(circ.depth(), 0)

    def test_random_measure(self):
        """Test random circuit with final measurement.
        """
        width = depth = 3
        circ = random_circuit(width, depth, measure=True)
        self.assertEqual(circ.width(), 2*width)
        dag = circuit_to_dag(circ)
        for nd in list(dag.topological_op_nodes())[-width:]:
            self.assertIsInstance(nd.op, Measure)

    def test_random_circuit_conditional_reset(self):
        """Test generating random circuits with conditional and reset.
        """
        width = 1
        depth = 100
        circ = random_circuit(width, depth, conditional=True, reset=True)
        self.assertEqual(circ.width(), 2*width)
        self.assertIn('reset', circ.count_ops())
