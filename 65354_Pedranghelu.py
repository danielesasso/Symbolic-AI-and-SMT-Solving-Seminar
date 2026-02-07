from z3 import *

def CountingStrategy(nums, goal):

    solver = Optimize()

    # permutazione dei 6 numeri 
    # (ogni numero viene usato al massimo una volta)
    p = [Int(f"p{i}") for i in range(6)]
    for i in range(6):
        solver.add(And(p[i] >= 0, p[i] < 6))
    solver.add(Distinct(p))

    # Operazioni per i 5 step 
    # (0:+, 1:-, 2:*, 3:/)
    op = [Int(f"op{i}") for i in range(5)]
    for i in range(5):
        solver.add(And(op[i] >= 0, op[i] <= 3))

    # k = quanti numeri usiamo 
    # (da 1 a 6). 
    # Se k=1: solo iniziale.
    k = Int("k")
    solver.add(And(k >= 1, k <= 6))

    # valore del numero scelto a step i
    n = [Int(f"n{i}") for i in range(6)]
    for i in range(6):
        solver.add(n[i] == Sum([If(p[i] == j, nums[j], 0) for j in range(6)]))

    # sempre interi positivi
    r = [Int(f"r{i}") for i in range(6)]
    solver.add(r[0] == n[0], r[0] > 0)

    def apply(a, b, o):
        # vincoli per divisione esatta e positività
        return If(o == 0, a + b,
               If(o == 1, a - b,
               If(o == 2, a * b,
                        a / b)))

    for i in range(1, 6):
        active = (i < k)  # se i<k, stiamo usando il numero n[i]
        a, b, o = r[i-1], n[i], op[i-1]

        # vincoli operazione valida 
        div_ok = And(b != 0, a % b == 0, a / b > 0)
        sub_ok = (a - b > 0)

        valid_op = Or(
            o == 0,                 # caso +
            And(o == 1, sub_ok),    # caso -
            o == 2,                 # caso *
            And(o == 3, div_ok)     # caso /
        )

        solver.add(If(active, valid_op, True))
        solver.add(r[i] == If(active, apply(a, b, o), a))
        solver.add(r[i] > 0)

    final = r[5]  # se k<6 resta uguale
    dist = Int("dist")
    solver.add(dist == If(final >= goal, final - goal, goal - final))

    # ottimizzazione: distanza
    solver.minimize(dist)

     # ottimizzazione: numeri usati
    solver.minimize(k)

    if solver.check() != sat:
        print("impossibile con questi vincoli.")
        return None

    m = solver.model()

    # strategia
    perm = [m.evaluate(p[i]).as_long() for i in range(6)]
    used = m.evaluate(k).as_long()
    ops = [m.evaluate(op[i]).as_long() for i in range(5)]
    rs = [m.evaluate(r[i]).as_long() for i in range(6)]
    chosen = [nums[perm[i]] for i in range(6)]

    sym = {0:"+", 1:"-", 2:"*", 3:"/"}

    print(f"Initial number: {chosen[0]}")
    step = 1
    for i in range(1, used):
        print(f"Step {step}: operation {sym[ops[i-1]]} with number {chosen[i]} -> result {rs[i]}")
        step += 1
    print(f"Final number: {rs[used-1]}")
    print(f"Distance from goal: {m.evaluate(dist)}")

    return True


# esempio:
CountingStrategy([1, 3, 5, 8, 10, 50], 462)
