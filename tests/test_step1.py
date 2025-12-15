from aste404_miniproject.gas_dynamics import (
    area_mach_relation, 
    normal_shock_relations,
    solve_expansion_fan,
    solve_oblique_beta
)
from aste404_miniproject.solver import HybridSolver

def run_tests():
    gamma = 1.4
    print("=== STEP 1 VERIFICATION ===")
    
    # 1. Test Solver & Isentropic Relation
    print("\n[1] Testing Solver on Isentropic Relation...")
    # Find Mach for A/A* = 2.0 (Supersonic)
    # Theoretical answer approx 2.197
    func = lambda m: area_mach_relation(m, gamma) - 2.0
    
    # We need the derivative for the Hybrid Solver
    # (We could import it, or define finite diff here)
    def deriv(m):
        h=1e-5
        return (area_mach_relation(m+h, gamma) - area_mach_relation(m, gamma))/h

    solver = HybridSolver()
    M_sol = solver.solve(func, deriv, guess=2.5, low=1.0, high=5.0)
    print(f"   Target A/A*=2.0. Calculated Mach: {M_sol:.4f}")
    assert abs(M_sol - 2.197) < 1e-2, "Solver Failed!"
    
    # 2. Test Normal Shock
    print("\n[2] Testing Normal Shock...")
    # M1 = 2.0. Expect M2 = 0.577
    res = normal_shock_relations(2.0, gamma)
    print(f"   M1=2.0 -> M2={res['M2']:.4f}")
    assert abs(res['M2'] - 0.577) < 1e-2, "Normal Shock Failed!"

    # 3. Test Expansion Fan
    print("\n[3] Testing Expansion Fan...")
    # M1=2.0, Turn 10 deg.
    # nu(2.0) = 26.38 deg. Target nu = 36.38. M2 should be ~2.38
    M2 = solve_expansion_fan(2.0, 10.0, gamma)
    print(f"   M1=2.0, Theta=10 -> M2={M2:.4f}")
    assert M2 > 2.0, "Expansion Fan Failed!"

    # 4. Test Oblique Shock
    print("\n[4] Testing Oblique Shock (Theta-Beta-M)...")
    # M1=2.0, Turn 10 deg.
    # Beta should be approx 39.3 deg
    beta = solve_oblique_beta(2.0, 10.0, gamma)
    print(f"   M1=2.0, Theta=10 -> Beta={beta:.4f}")
    assert abs(beta - 39.3) < 1.0, "Oblique Shock Failed!"
    
    print("\nAll Step 1 tests passed successfully.")

if __name__ == "__main__":
    run_tests()