from z3 import *

def CountingStrategy(nums, goal):

    s = Solver()

    # permutazione dei 6 numeri (ogni numero al massimo una volta)
    p = [Int(f"p{i}") for i in range(6)]
    for i in range(6):
        s.add(p[i] >= 0, p[i] < 6)
    s.add(Distinct(p))

    # operazioni per i 5 step (0:+, 1:-, 2:*, 3:/)
    op = [Int(f"op{i}") for i in range(5)]
    for i in range(5):
        s.add(op[i] >= 0, op[i] <= 3)

    # k = quanti numeri usiamo
    k = Int("k")
    s.add(k >= 1, k <= 6)

    # numero scelto a step i
    n = [Int(f"n{i}") for i in range(6)]
    for i in range(6):
        expr = nums[5]
        for j in range(4, -1, -1):
            expr = If(p[i] == j, nums[j], expr)
        s.add(n[i] == expr)

    # risultati intermedi
    r = [Int(f"r{i}") for i in range(6)]
    s.add(r[0] == n[0])

    def apply(a, b, o):
        return If(o == 0, a + b,
               If(o == 1, a - b,
               If(o == 2, a * b,
                        a / b)))

    for i in range(1, 6):
        active = (i < k)
        a, b, o = r[i-1], n[i], op[i-1]

        # divisione solo se esatta
        div_ok = And(b != 0, a % b == 0)
        valid_op = Or(o != 3, div_ok)

        s.add(Implies(active, valid_op))
        s.add(r[i] == If(active, apply(a, b, o), a))

    # distanza dal goal
    final = r[5]
    dist = Int("dist")
    s.add(dist == If(final >= goal, final - goal, goal - final))

    best_model = None
    best_dist = None
    best_k = None

    def m_int(m, e):
        return int(str(m.evaluate(e, model_completion=True)))

    while s.check() == sat:
        m = s.model()
        d = m_int(m, dist)
        kk = m_int(m, k)

        if best_model is None or d < best_dist or (d == best_dist and d == 0 and kk < best_k):
            best_model, best_dist, best_k = m, d, kk

        # vincolo per trovare di meglio:
        # - se non abbiamo dist==0: cerchiamo dist più piccolo
        # - se dist==0: cerchiamo k più piccolo 
        if d == 0:
            s.add(k < kk)
        else:
            s.add(dist < d)

    if best_model is None:
        print("No solution found.")
        return None

    # estrazione dati
    perm = [m_int(best_model, p[i]) for i in range(6)]
    used = m_int(best_model, k)
    ops  = [m_int(best_model, op[i]) for i in range(5)]
    rs   = [m_int(best_model, r[i]) for i in range(6)]
    chosen = [nums[perm[i]] for i in range(6)]

    sym = {0:"+", 1:"-", 2:"*", 3:"/"}

    print(f"Initial number: {chosen[0]}")
    step = 1
    for i in range(1, used):
        print(f"Step {step}: operation {sym[ops[i-1]]} with number {chosen[i]} -> result {rs[i]}")
        step += 1
    print(f"Final number: {rs[used-1]}")
    print(f"Distance from goal: {best_dist}")


# esempio:
CountingStrategy([1, 3, 5, 8, 10, 50], 462)
