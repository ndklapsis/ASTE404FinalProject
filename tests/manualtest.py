from aste404_miniproject import gas_dynamics

# Calculate characteristic velocity (c*)
c_star = gas_dynamics.c_star(gamma=1.2, r=287, t0=2800)
print(f"Characteristic velocity: {c_star:.1f} m/s")

# Get isentropic pressure ratio at a given Mach
P_ratio = gas_dynamics.isentropic_P_P0(M=2.5, gamma=1.4)
print(f"P/P0 at M=2.5: {P_ratio:.4f}")

# Normal shock relations
shock = gas_dynamics.normal_shock_relations(M1=2.5, gamma=1.4)
print(f"Post-shock Mach: {shock['M2']:.3f}")
print(f"Pressure ratio: {shock['P2_P1']:.3f}")