"""Three in-place sorts. Compare keys only; never use tags as tie-breakers."""
from dataclasses import dataclass

@dataclass
class Stats:
    comparisons: int = 0
    writes: int = 0

def greater(x, y, key, stats):
    if stats is not None:
        stats.comparisons += 1
    return key(x) > key(y)

def swap(a, i, j, stats):
    a[i], a[j] = a[j], a[i]
    if stats is not None:
        stats.writes += 2

def identity(x):
    return x

def insertion_sort(a, key=identity, stats=None):
    """Insert each item into its sorted prefix; strict > preserves ties."""
    for i in range(1, len(a)):
        value = a[i]
        j = i - 1
        while j >= 0:
            if not greater(a[j], value, key, stats):
                break
            a[j + 1] = a[j]
            if stats is not None:
                stats.writes += 1
            j -= 1
        a[j + 1] = value
        if stats is not None:
            stats.writes += 1

def bubble_sort(a, key=identity, stats=None):
    """Shrink the active prefix and stop after a pass with no swaps."""
    for end in range(len(a) - 1, 0, -1):
        changed = False
        for j in range(end):
            if greater(a[j], a[j + 1], key, stats):
                swap(a, j, j + 1, stats)
                changed = True
        if not changed:
            break

def sift_down(a, root, size, key, stats):
    """Restore a max-heap within a[0:size]; size is an exclusive bound."""
    while 2 * root + 1 < size:
        child = 2 * root + 1
        if child + 1 < size and greater(a[child + 1], a[child], key, stats):
            child += 1
        if not greater(a[child], a[root], key, stats):
            break
        swap(a, root, child, stats)
        root = child

def heap_sort(a, key=identity, stats=None):
    """Floyd heap construction followed by repeated maximum extraction."""
    n = len(a)
    for root in range(n // 2 - 1, -1, -1):
        sift_down(a, root, n, key, stats)
    for end in range(n - 1, 0, -1):
        swap(a, 0, end, stats)
        sift_down(a, 0, end, key, stats)

ALGORITHMS = {'Insertion': insertion_sort, 'Bubble': bubble_sort, 'Heap': heap_sort}
