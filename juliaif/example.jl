using PyCall

cirq = pyimport("cirq")

# God bless stackoverflow
# https://github.com/JuliaPy/PyCall.jl/issues/48
py"""
import sys
sys.path.insert(0, "..")
"""
icm = pyimport("icm")

#import icm.icm_flag_manipulations as flags
a = icm.SplitQubit("a")
b = icm.SplitQubit("b")

mycircuit = cirq.Circuit(cirq.T.on(a), cirq.T.on(b), cirq.CNOT.on(a,b), cirq.S.on(a))
icm.icm_flag_manipulations.add_op_ids(mycircuit, [cirq.T, cirq.S])

print(mycircuit)

icm_circuit = cirq.Circuit(cirq.decompose(mycircuit,
                                          intercepting_decomposer=icm.decomp_to_icm,
                                          keep = icm.keep_icm))
print(icm_circuit)