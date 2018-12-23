from trace import Trace
from instruction import Instruction
from z3 import *


# evil caller
EVIL_CALLER = Trace()
instr0 = Instruction("MSTORE")
instr1 = Instruction("MSTORE")
instr2 = Instruction("SHA3")
instr3 = Instruction("SLOAD")
instr3.add_operand(BitVec("some_var_1", 256))
instr4 = Instruction("MLOAD")
instr5 = Instruction("MLOAD")
instr6 = Instruction("CALL")
instr6.add_operand(Concat(BitVecVal(0, 96), Extract(159, 0, BitVec("Is", 256))))
instr6.add_operand(BitVec("Ia_store-some_var_1-balances[msg.sender]", 256))
instr7 = Instruction("MSTORE")
instr8 = Instruction("MSTORE")
instr9 = Instruction("SHA3")
instr10 = Instruction("SSTORE")
instr10.add_operand(BitVec("some_var_1", 256))
instr10.add_operand(0)
EVIL_CALLER.add_to_trace(instr0)
EVIL_CALLER.add_to_trace(instr1)
EVIL_CALLER.add_to_trace(instr2)
EVIL_CALLER.add_to_trace(instr3)
EVIL_CALLER.add_to_trace(instr4)
EVIL_CALLER.add_to_trace(instr5)
EVIL_CALLER.add_to_trace(instr6)
EVIL_CALLER.add_to_trace(instr7)
EVIL_CALLER.add_to_trace(instr8)
EVIL_CALLER.add_to_trace(instr9)
EVIL_CALLER.add_to_trace(instr10)
