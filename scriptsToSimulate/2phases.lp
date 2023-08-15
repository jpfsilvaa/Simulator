\ Model 2nd phase allocation
\ LP format - for model browsing. Use MPS format to capture full model detail.
Maximize
  x_v18_c8 + x_v21_c0 + x_v23_c8 + 0 x_s_v18 + 0 x_s_v21 + 0 x_s_v23
Subject To
 nonAllocated_v18: x_v18_c8 <= 1
 nonAllocated_v21: x_v21_c0 <= 1
 nonAllocated_v23: x_v23_c8 <= 1
 allocated_v0: x_v0_c40 = 1
 allocated_v6: x_v6_c3 + x_v6_c44 = 1
 allocated_v10: x_v10_c8 = 1
 allocated_v13: x_v13_c40 = 1
 allocated_v14: x_v14_c3 + x_v14_c44 = 1
 allocated_v24: x_v24_c40 = 1
 allocated_v25: x_v25_c40 = 1
 allocated_v78: x_v78_c8 = 1
 capacity_c0: <= 0
 capacity_c1: <= 0
 capacity_c2: <= 0
 capacity_c3: <= 0
 capacity_c4: <= 0
 capacity_c5: <= 0
 capacity_c6: <= 0
 capacity_c7: <= 0
 capacity_c8: x_c8_sink_cc8_0 + x_c8_sink_cc8_1 <= 2
 capacity_c9: <= 0
 capacity_c10: <= 0
 capacity_c11: <= 0
 capacity_c12: <= 0
 capacity_c13: <= 0
 capacity_c14: <= 0
 capacity_c15: <= 0
 capacity_c16: <= 0
 capacity_c17: <= 0
 capacity_c18: <= 0
 capacity_c19: <= 0
 capacity_c20: <= 0
 capacity_c21: <= 0
 capacity_c22: <= 0
 capacity_c23: <= 0
 capacity_c24: <= 0
 capacity_c25: <= 0
 capacity_c26: <= 0
 capacity_c27: <= 0
 capacity_c28: <= 0
 capacity_c29: <= 0
 capacity_c30: <= 0
 capacity_c31: <= 0
 capacity_c32: <= 0
 capacity_c33: <= 0
 capacity_c34: <= 0
 capacity_c35: <= 0
 capacity_c36: <= 0
 capacity_c37: <= 0
 capacity_c38: <= 0
 capacity_c39: <= 0
 capacity_c40: x_c40_sink_cc40_0 + x_c40_sink_cc40_1 + x_c40_sink_cc40_2
   + x_c40_sink_cc40_3 <= 4
 capacity_c41: <= 0
 capacity_c42: <= 0
 capacity_c43: <= 0
 capacity_c44: x_c44_sink_cc44_0 + x_c44_sink_cc44_1 <= 2
Bounds
Binaries
 x_v0_c40 x_v6_c3 x_v6_c44 x_v10_c8 x_v13_c40 x_v14_c3 x_v14_c44 x_v24_c40
 x_v25_c40 x_v78_c8 x_v18_c8 x_v21_c0 x_v23_c8 x_s_v18 x_s_v21 x_s_v23
 x_c8_sink_cc8_0 x_c8_sink_cc8_1 x_c40_sink_cc40_0 x_c40_sink_cc40_1
 x_c40_sink_cc40_2 x_c40_sink_cc40_3 x_c44_sink_cc44_0 x_c44_sink_cc44_1
End
