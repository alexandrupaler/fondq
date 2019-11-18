import cirq

class ReplaceHadamards(cirq.PointOptimizer):
    """
    Replaces  opposite rotations with identity.
    """
    def optimization_at(self, circuit, index, op):

        if not (isinstance(op, cirq.GateOperation) and (op.gate == cirq.H)):
            return None

        n_idx = circuit.next_moment_operating_on(op.qubits, index + 1)
        if n_idx is None:
            return None

        next_op = circuit.operation_at(op.qubits[0], n_idx)

        if next_op.gate == cirq.H:
            return cirq.PointOptimizationSummary(clear_span= n_idx - index + 1,
                                            clear_qubits=op.qubits,
                                            new_operations=[])# Two opposite rotations are erased

        return None

class CNOTOptimizer(cirq.PointOptimizer):
    """Replaces CNOTs and Hadamards with a CNOT with inverse direction"""

    # The circuit to improve
    # The index of the moment with the operation to focus on
    # The operation to focus improvements upon
    def optimization_at(self, circuit, index, op):

        # Is the gate an X gate?
        if index > 0 and isinstance(op, cirq.GateOperation) and (op.gate == cirq.CNOT):

            # print("found a CNOT")

            """
            Checking for the Hadamards
            """
            control_qubit = op.qubits[0]
            target_qubit = op.qubits[1]

            # is the next gate a cnot?
            nxt_1 = circuit.next_moment_operating_on([control_qubit],
                                                     start_moment_index=index + 1,
                                                     max_distance=1)
            if nxt_1 is None:
                return None

            nxt_2 = circuit.next_moment_operating_on([target_qubit],
                                                     start_moment_index=index + 1,
                                                     max_distance=1)
            if nxt_2 is None:
                return None

            # Get the operation at the next index
            next_op_h1 = circuit.operation_at(control_qubit, nxt_1)
            next_op_h2 = circuit.operation_at(target_qubit, nxt_2)

            # print("next are ", next_op_h1, next_op_h2)

            # Are the operations Hadamards?
            if isinstance(next_op_h1, cirq.GateOperation) and (next_op_h1.gate == cirq.H) \
                    and isinstance(next_op_h2, cirq.GateOperation) and (next_op_h2.gate == cirq.H) :

                # theoretically nxt_1 and nxt_2 should be equal
                if (nxt_1 != nxt_2):
                    # print(nxt_1, nxt_2)
                    return None

                # If yes, replace the CNOT with a reversed CNOT
                new_ops = [cirq.H.on(control_qubit),
                           cirq.H.on(target_qubit),
                           cirq.CNOT(target_qubit, control_qubit)]

                # see https://cirq.readthedocs.io/en/stable/generated/cirq.PointOptimizationSummary.html?highlight=pointoptimizationsummary
                return cirq.PointOptimizationSummary(
                    clear_span=nxt_1 - index + 1,  # Range of moments to affect.
                    clear_qubits=op.qubits,  # The set of qubits that should be cleared with each affected moment
                    new_operations=new_ops # The operations to replace
                )