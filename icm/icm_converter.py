"""
NOTE: Experimental code for testing how gate decomposition that introduces
introduces ancillas would look like in Cirq

For this the ICM form of circuits is being implemented. As described in

"Faster manipulation of large quantum circuits using wire label reference
diagrams" https://arxiv.org/abs/1811.06011
"""

import cirq

from icm.icm_operation_id import OperationId

class SplitQubit(cirq.NamedQubit):

    # Static nr_ancilla
    nr_ancilla = -1


    def __init__(self, name):
        super().__init__(name)

        self.children = (None, None)

        self.threshold = OperationId()

    def get_latest_ref(self, operation_id):

        # this wire has not been split
        if self.children == (None, None):
            return self

        n_ref = self
        while n_ref.children != (None, None):
            # Decide based on the threshold
            if n_ref.threshold >= operation_id:
                n_ref = self.children[0]
            else:
                n_ref = self.children[1]

        return n_ref

    def split_this_wire(self, operation_id):
        # It can happen that the reference is too old
        current_wire = self.get_latest_ref(operation_id)

        # The wire receives a threshold for latter updates
        current_wire.threshold = operation_id

        # It is a new wire, but keep the old name
        n_child_0 = SplitQubit(current_wire.name)

        # It is a new wire, that is introduced and gets a new name
        SplitQubit.nr_ancilla += 1
        n_child_1 = SplitQubit("_anc_{0}".format(SplitQubit.nr_ancilla))

        # Update the children tuple of this wire
        current_wire.children = (n_child_0, n_child_1)

        # Return the children as a tuple
        return current_wire.children


def decomp_to_icm(cirq_operation):
    # TODO:

    new_op_id = cirq_operation.icm_op_id.add_decomp_level()

    # Assume for the moment that these are only single qubit operations
    new_wires = cirq_operation.qubits[0].split_this_wire(new_op_id)

    print("qubit is ", cirq_operation.qubits[0])

    # Create the cnot
    cnot = cirq.CNOT(new_wires[0], new_wires[1])
    # Assign a decomposition id, like [old].1
    cnot.icm_op_id = new_op_id.advance_decomp()

    # Create the measurement
    meas = cirq.measure(new_wires[0])
    # Because this operation follows the CNOT, has ID from the previous
    # results into something like  [oldid].2
    meas.icm_op_id = cnot.icm_op_id.advance_decomp()

    return [cnot, meas]


def keep_icm(op):
    # TODO: mai calumea
    if isinstance(op.gate, (cirq.CNotPowGate, cirq.MeasurementGate)):
        return True

    return False

import icm.icm_flag_manipulations as flags
a = SplitQubit("a")
b = SplitQubit("b")

mycircuit = cirq.Circuit(cirq.T.on(a), cirq.T.on(b), cirq.CNOT.on(a,b), cirq.S.on(a))
flags.add_op_ids(mycircuit, [cirq.T, cirq.S])

print(mycircuit)

icm_circuit = cirq.Circuit(cirq.decompose(mycircuit,
                                          intercepting_decomposer=decomp_to_icm,
                                          keep = keep_icm))
print(icm_circuit)