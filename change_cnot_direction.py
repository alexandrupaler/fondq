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

def is_cnot_with_decomposed_flag(op):
    if op.gate == cirq.CNOT:
        return hasattr(op, "decomposed")
    return False

def reset_decomposition_flag(circuit):
    for op in circuit.all_operations():
        if is_cnot_with_decomposed_flag(op):
            op.decomposed = False

def mydecomposer(op):
    if isinstance(op, cirq.GateOperation) and (op.gate == cirq.CNOT):
        control_q = op.qubits[0]
        target_q = op.qubits[1]

        cnot = cirq.CNOT.on(target_q, control_q)
        if not is_cnot_with_decomposed_flag(cnot):
            setattr(cnot, "decomposed", True)

        decomps = [cirq.H.on(control_q), cirq.H.on(target_q),
                   cnot,
                   cirq.H.on(control_q), cirq.H.on(target_q)]
        return decomps

def need_to_keep(op):
    if isinstance(op, cirq.GateOperation):
        if op.gate == cirq.H:
            return True
        if is_cnot_with_decomposed_flag(op):
            return op.decomposed
    return False

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
reset_decomposition_flag(circ2)

# Generate a new circuit from the previously decomposed one
circ3 = cirq.Circuit(cirq.decompose(circ2,
                     intercepting_decomposer=mydecomposer,
                     keep=need_to_keep))
print(circ3)

