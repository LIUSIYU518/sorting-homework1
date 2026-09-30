"""Small numerical example from the instructor's screenshots."""
import json
from pathlib import Path
from sorting import ALGORITHMS, Stats

class TraceList(list):
    def __init__(self, values):
        super().__init__(values)
        self.trace = []
    def __setitem__(self, index, value):
        super().__setitem__(index, value)
        self.trace.append(list(self))

def main():
    source = [5, 1, 4, 2]
    result = {'input': source, 'algorithms': {}}
    for name, fn in ALGORITHMS.items():
        a = TraceList(source)
        stats = Stats()
        fn(a, stats=stats)
        assert list(a) == [1, 2, 4, 5]
        result['algorithms'][name] = dict(output=list(a), comparisons=stats.comparisons,
            writes=stats.writes, assignment_trace=a.trace)
        print(name, list(a), 'comparisons:', stats.comparisons, 'array writes:', stats.writes)
    Path('results').mkdir(exist_ok=True)
    Path('results/demo.json').write_text(json.dumps(result, indent=2))

if __name__ == '__main__':
    main()
