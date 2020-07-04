# -*- coding: utf-8 -*-

# This code is part of Qiskit.
#
# (C) Copyright IBM 2019.
#
# This code is licensed under the Apache License, Version 2.0. You may
# obtain a copy of this license in the LICENSE.txt file in the root directory
# of this source tree or at http://www.apache.org/licenses/LICENSE-2.0.
#
# Any modifications or derivative works of this code must retain this
# copyright notice, and modified files need to carry a notice indicating
# that they have been altered from the originals.

"""
Convenience entry point into pulse scheduling, requiring only a circuit and a backend. For more
control over pulse scheduling, look at `qiskit.scheduler.schedule_circuit`.
"""
import logging

from time import time
from typing import List, Optional, Union

from qiskit.circuit.quantumcircuit import QuantumCircuit
from qiskit.exceptions import QiskitError
from qiskit.pulse import InstructionScheduleMap, Schedule
from qiskit.providers import BaseBackend
from qiskit.scheduler import ScheduleConfig
from qiskit.scheduler.schedule_circuit import schedule_circuit
from qiskit.transpiler.instruction_durations import InstructionDurations, InstructionDurationsType

LOG = logging.getLogger(__name__)


def _log_schedule_time(start_time, end_time):
    log_msg = "Total Scheduling Time - %.5f (ms)" % ((end_time - start_time) * 1000)
    LOG.info(log_msg)


def schedule(circuits: Union[QuantumCircuit, List[QuantumCircuit]],
             backend: Optional[BaseBackend] = None,
             inst_map: Optional[InstructionScheduleMap] = None,
             meas_map: Optional[List[List[int]]] = None,
             instruction_durations: Optional[InstructionDurationsType] = None,
             dt: Optional[float] = None,
             method: Optional[Union[str, List[str]]] = None) -> Union[Schedule, List[Schedule]]:
    """
    Schedule a circuit to a pulse ``Schedule``, using the backend, according to any specified
    methods. Supported methods are documented in :py:mod:`qiskit.scheduler.schedule_circuit`.

    Args:
        circuits: The quantum circuit or circuits to translate
        backend: A backend instance, which contains hardware-specific data required for scheduling
        inst_map: Mapping of circuit operations to pulse schedules. If ``None``, defaults to the
                  ``backend``\'s ``instruction_schedule_map``
        meas_map: List of sets of qubits that must be measured together. If ``None``, defaults to
                  the ``backend``\'s ``meas_map``
        instruction_durations: Durations of instructions. Duration must be the number of ``dt``s.
            Note that ``dt`` depends on backend configuration. Instruction is specified by
            a pair of basic instruction name and its acting physical qubits.
            E.g. [('cx', [0, 1], 1000), ('u3', [0], 300)]
            Durations defined in ``backend.properties`` are used as default and
            they are overwritten with the instruction_durations.
            Note: The durations must coincide with durations of schedules defined in inst_map.
        dt: For scheduled circuits which contain time information, dt is required. If not provided,
            it will be obtained from the backend configuration
        method: Optionally specify a particular scheduling method

    Returns:
        A pulse ``Schedule`` that implements the input circuit

    Raises:
        QiskitError: If ``inst_map`` and ``meas_map`` are not passed and ``backend`` is not passed
    """
    start_time = time()
    if inst_map is None:
        if backend is None:
            raise QiskitError("Must supply either a backend or InstructionScheduleMap for "
                              "scheduling passes.")
        defaults = backend.defaults()
        if defaults is None:
            raise QiskitError("The backend defaults are unavailable. The backend may not "
                              "support pulse.")
        inst_map = defaults.instruction_schedule_map
    if meas_map is None:
        if backend is None:
            raise QiskitError("Must supply either a backend or a meas_map for scheduling passes.")
        meas_map = backend.configuration().meas_map
    if instruction_durations is None:
        if backend is None:
            raise QiskitError("Must supply either a backend or a instruction_durations for "
                              "scheduling passes.")
        instruction_durations = InstructionDurations.from_backend(backend)
    if dt is None:
        if backend is not None:
            dt = backend.configuration().dt

    schedule_config = ScheduleConfig(inst_map=inst_map, meas_map=meas_map, dt=dt)
    circuits = circuits if isinstance(circuits, list) else [circuits]
    for circ in circuits:
        circ.instruction_durations = instruction_durations
    schedules = [schedule_circuit(circuit, schedule_config, method) for circuit in circuits]
    end_time = time()
    _log_schedule_time(start_time, end_time)
    return schedules[0] if len(schedules) == 1 else schedules
