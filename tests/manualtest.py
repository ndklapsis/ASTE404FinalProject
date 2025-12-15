from aste404_miniproject.gas_dynamics import *

gamma = 1.4

# 2. Test Normal Shock
print("\n[2] Testing Normal Shock...")
# M1 = 2.0. Expect M2 = 0.577
res = normal_shock_relations(2.0, gamma)
print(res)


CF = c_f(gamma, pe_p0=0.1, pa_p0=0.05, ae_at=5.0)
print(f"\nCalculated Thrust Coefficient CF: {CF:.4f}")
