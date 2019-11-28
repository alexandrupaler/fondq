import cirq

"""
This is experimental code to investigate and to show how gate decompositions
could be used for the implementation of gate identities used during circuit
optimisations.

In the following the direction of a CNOT is changed by using an intercepting
decomposer and a keep predicate. The cirq.decompose protocol is recursive and 
decomposising a gate A into the same gate A will result in endless loops. To 
stop the endless loops, the operations will be flagged with a Boolean attribute.
"""

"""
    FLAG MANIPULATIONS
"""
def is_op_with_decomposed_flag(op, gate_type):
    if op.gate == gate_type:
        return hasattr(op, "decomposed")
    return False

def reset_decomposition_flags(circuit, gate_type):
    for op in circuit.all_operations():
        if is_op_with_decomposed_flag(op, gate_type):
            op.decomposed = False

def add_decomposition_flags(circuit, gate_type):
    for op in circuit.all_operations():
        if not is_op_with_decomposed_flag(op, gate_type):
            setattr(op, "decomposed", True)

def remove_decomposition_flags(circuit, gate_type):
    for op in circuit.all_operations():
        if is_op_with_decomposed_flag(op, gate_type):
            delattr(op, "decomposed")

"""
    DECOMPOSITION RULE(S)
"""

def mydecomposer(op):
    if isinstance(op, cirq.GateOperation) and (op.gate == cirq.CNOT):
        control_q = op.qubits[0]
        target_q = op.qubits[1]

        cnot = cirq.CNOT.on(target_q, control_q)

        if not is_op_with_decomposed_flag(cnot, cirq.CNOT):
            setattr(cnot, "decomposed", True)

        decomps = [cirq.H.on(control_q), cirq.H.on(target_q),
                   cnot,
                   cirq.H.on(control_q), cirq.H.on(target_q)]
        return decomps

def need_to_keep(op):
    if isinstance(op, cirq.GateOperation):
        if op.gate == cirq.H:
            return True
        if is_op_with_decomposed_flag(op, cirq.CNOT):
            return op.decomposed
    return False

"""
    MAIN 
"""
# Create three qubits
a = cirq.NamedQubit("a")
b = cirq.NamedQubit("b")
c = cirq.NamedQubit("c")

# and a circuit consisting of a single CNOT
circuit = cirq.Circuit([cirq.H.on(a), cirq.H.on(b),
                        cirq.CNOT.on(a, b),
                        cirq.H.on(a), cirq.H.on(b)])

print(circuit)

# change the direction of the CNOT by using a recursive decomposition
# In theory Cirq does not support cycles in the decomposition, because endless
# loops would result. We can stop the decomposition by flagging the gates
print("flipped the CNOT...")
circ2 = cirq.Circuit(cirq.decompose(circuit,
                     intercepting_decomposer=mydecomposer,
                     keep=need_to_keep))
print(circ2)

# The resulting CNOTs cannot be decomposed again because these are flagged
print("nothing changes except the flags are reset")

# Reset the flags
reset_decomposition_flags(circ2, cirq.CNOT)

# Generate a new circuit from the previously decomposed one
circ3 = cirq.Circuit(cirq.decompose(circ2,
                     intercepting_decomposer=mydecomposer,
                     keep=need_to_keep))
print(circ3)

remove_decomposition_flags(circ3, cirq.CNOT)

