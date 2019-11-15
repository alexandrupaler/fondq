import cirq

"""
    Grover implementation begin
"""
def set_io_qubits(qubit_count):
    """Add the specified number of input and output qubits."""
    input_qubits = [cirq.GridQubit(i, 0) for i in range(qubit_count)]
    output_qubit = cirq.GridQubit(qubit_count, 0)
    #
    return (input_qubits, output_qubit)


def make_oracle(input_qubits, output_qubit, x_bits):
    """Implement function {f(x) = 1 if x==x', f(x) = 0 if x!= x'}."""
    # Make oracle.
    # for (1, 1) it's just a Toffoli gate
    # otherwise negate the zero-bits.
    yield(cirq.X(q) for (q, bit) in zip(input_qubits, x_bits) if not bit)
    yield(cirq.TOFFOLI(input_qubits[0], input_qubits[1], output_qubit))
    yield(cirq.X(q) for (q, bit) in zip(input_qubits, x_bits) if not bit)


def make_grover_circuit(input_qubits, output_qubit, oracle):
    """Find the value recognized by the oracle in sqrt(N) attempts."""
    # For 2 input qubits, that means using Grover operator only once.

    # Initialize qubits.
    yield ([
        cirq.X(output_qubit),
        cirq.H(output_qubit),
        cirq.H.on_each(*input_qubits),
    ])

    # Query oracle.
    yield from oracle

    # Construct Grover operator.
    yield cirq.H.on_each(*input_qubits)
    yield cirq.X.on_each(*input_qubits)
    yield cirq.H.on(input_qubits[1])
    yield cirq.CNOT(input_qubits[0], input_qubits[1])
    yield cirq.H.on(input_qubits[1])
    yield cirq.X.on_each(*input_qubits)
    yield cirq.H.on_each(*input_qubits)

    # Measure the result.
    yield cirq.measure(*input_qubits, key='result')


def bitstring(bits):
    return ''.join(str(int(b)) for b in bits)

"""
Grover implementation end
"""