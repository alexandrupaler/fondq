import cirq
import cirq.ops as ops

class FondQDevice(cirq.Device):
    def __init__(self, sizex, sizey):

        self.qubits = []
        for i in range(sizex):
            for j in range(sizey):
                self.qubits.append(cirq.GridQubit(i, j))

    def duration_of(self, operation):
        if ops.op_gate_of_type(operation, ops.HPowGate):
            return cirq.Duration(nanos=10)
        if ops.op_gate_of_type(operation, ops.ZPowGate):
            return cirq.Duration(nanos=10)
        if ops.op_gate_of_type(operation, ops.CNotPowGate):
            return cirq.Duration(nanos=200)
        if ops.op_gate_of_type(operation, ops.MeasurementGate):
            return cirq.Duration(nanos=100)

        raise ValueError('Unsupported gate type: {!r}'.format(operation))

    def decompose_operation(self, operation):

        # Known gate name
        if not isinstance(operation, ops.GateOperation):
            raise TypeError("{!r} is not a gate operation.".format(operation))

        if self.is_fondq_device_gate(operation):
            return operation

        if isinstance(operation.gate, (ops.XPowGate)):
            return [cirq.H.on(operation.qubits[0]),
                    cirq.Z(operation.qubits[0]),
                    cirq.H.on(operation.qubits[0])]

        if isinstance(operation.gate, (ops.CZPowGate)):
            # I am not checking for the exponent to simplify code
            return [cirq.H.on(operation.qubits[0]),
                    cirq.CNOT(*operation.qubits),
                    cirq.H.on(operation.qubits[0])]

        if isinstance(operation.gate, cirq.ops.CCXPowGate):
            # The Toffoli is decomposed into CCZ and Hadamard
            #   -> see cirq.CCXPowGate._decompose
            # afterwards the CCZ is decomposed into CNOT and RZ
            #   -> see cirq.CCZPowGate._decompose
            return cirq.decompose(operation, keep=self.is_fondq_device_gate)

        raise TypeError("Don't know how to work with {!r}. "
                        "It isn't a native Lisbon28Device operation, "
                        .format(operation.gate))
        #
        # return operation

    def is_fondq_device_gate(self, op):
        """
        Check if the gate is from the gate set supported by the device.
        Exponents are not checked.
        :param op:
        :return:
        """
        to_keep = isinstance(op.gate, (
            ops.CNotPowGate,
            ops.ZPowGate,
            ops.HPowGate,
            ops.MeasurementGate))
        return to_keep

    def validate_operation(self, operation):
        if not isinstance(operation, cirq.GateOperation):
            raise ValueError('{!r} is not a supported operation'.format(operation))

        if not self.is_fondq_device_gate(operation):
            raise ValueError('{!r} is not a supported gate'.format(operation.gate))

        # here we check connectivity?
        if len(operation.qubits) == 2:
            p, q = operation.qubits
            if not p.is_adjacent(q):
                # we could introduce automatic swap network
                raise ValueError('Non-local interaction: {}'.format(repr(operation)))

    def validate_scheduled_operation(self, schedule, scheduled_operation):
        self.validate_operation(scheduled_operation.operation)

    def validate_circuit(self, circuit):
        for moment in circuit:
            for operation in moment.operations:
                self.validate_operation(operation)

    def validate_schedule(self, schedule):
        for scheduled_operation in schedule.scheduled_operations:
            self.validate_scheduled_operation(schedule, scheduled_operation)
