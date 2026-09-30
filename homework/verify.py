"""Independent correctness oracle and genuine key-only stability checks."""
import itertools
import json
import random
from pathlib import Path
from sorting import ALGORITHMS, Stats

def main():
    rng = random.Random(20260930)
    cases = [list(x) for n in range(7) for x in itertools.product([-1, 0, 1], repeat=n)]
    cases += [[rng.randrange(-100, 101) for _ in range(rng.randrange(201))] for _ in range(100)]
    checks = 0
    for name, fn in ALGORITHMS.items():
        for source in cases:
            for counted in (False, True):
                a = source.copy()
                fn(a, stats=Stats() if counted else None)
                assert a == sorted(source), (name, source, a)
                checks += 1
    tagged = [(2, 'A'), (1, 'B'), (2, 'C'), (1, 'D'), (2, 'E')]
    outputs = {}
    for name, fn in ALGORITHMS.items():
        a = tagged.copy()
        fn(a, key=lambda item: item[0])
        assert [x[0] for x in a] == sorted(x[0] for x in tagged)
        outputs[name] = {'output': a, 'stable_on_example': a == sorted(tagged, key=lambda x: x[0])}
        if name != 'Heap':
            for source in cases:
                a = list(zip(source, range(len(source))))
                expected = sorted(a, key=lambda x: x[0])
                fn(a, key=lambda x: x[0])
                assert a == expected
    assert not outputs['Heap']['stable_on_example']
    result = {'integer_correctness_checks': checks, 'input_cases': len(cases), 'tagged_input': tagged, 'stability': outputs}
    Path('results').mkdir(exist_ok=True)
    Path('results/verification.json').write_text(json.dumps(result, indent=2))
    print(json.dumps(result, indent=2))

if __name__ == '__main__':
    main()
