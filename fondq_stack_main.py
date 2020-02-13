import random

# Import the Grover implementation
from grover_algorithm import *

# This is for the device
from fondq_device import FondQDevice

# This is for the optimisers
from cnotopt import CNOTOptimizer, ReplaceHadamards

"""
Start mapping and optimisation
"""
qubit_count = 2
# circuit_sample_count = 10

#Set up input and output qubits.
(input_qubits, output_qubit) = set_io_qubits(qubit_count)

#Choose the x' and make an oracle which can recognize it.
x_bits = [random.randint(0, 1) for _ in range(qubit_count)]
print('Secret bit sequence: {}'.format(x_bits))

# Make oracle (black box)
oracle = make_oracle(input_qubits, output_qubit, x_bits)

# Embed the oracle into a quantum circuit implementing Grover's algorithm.
# circuit = make_grover_circuit(input_qubits, output_qubit, oracle)
print('Circuit:')
circuit = cirq.Circuit(
    make_grover_circuit(input_qubits, output_qubit, oracle)
       ,device=FondQDevice(7, 4)
)
print(circuit)
print("\n")

# Make sure that the Hadamards are next to the CNOT
circuit_earliest = cirq.Circuit(circuit.all_operations())
#
print("Optimize the CNOTs\n")
cnotopt = CNOTOptimizer()
cnotopt.optimize_circuit(circuit_earliest)
print(circuit_earliest)
# #
print("Replace Hadamards\n")
hopt = ReplaceHadamards()
hopt.optimize_circuit(circuit_earliest)
print(circuit_earliest)
#
print("Reinsert all the gates\n")
circuit_earliest = cirq.Circuit(circuit_earliest.all_operations())
print(circuit_earliest)

print("\nRemove empty moments")
remempty = cirq.DropEmptyMoments()
remempty.optimize_circuit(circuit_earliest)
print(circuit_earliest)

