"""Binary search + a recorder that writes down every move so the UI can replay it."""

MODES = ("any", "first", "last")


def binary_search(a, target):
    """Index of any match, or -1."""
    lo, hi = 0, len(a) - 1
    while lo <= hi:
        mid = (lo + hi) // 2
        if a[mid] == target:
            return mid
        elif a[mid] < target:
            lo = mid + 1
        else:
            hi = mid - 1
    return -1


def first_occurrence(a, target):
    lo, hi, ans = 0, len(a) - 1, -1
    while lo <= hi:
        mid = (lo + hi) // 2
        if a[mid] == target:
            ans = mid
            hi = mid - 1  # maybe an earlier copy exists, keep going left
        elif a[mid] < target:
            lo = mid + 1
        else:
            hi = mid - 1
    return ans


def last_occurrence(a, target):
    lo, hi, ans = 0, len(a) - 1, -1
    while lo <= hi:
        mid = (lo + hi) // 2
        if a[mid] == target:
            ans = mid
            lo = mid + 1  # same idea but going right
        elif a[mid] < target:
            lo = mid + 1
        else:
            hi = mid - 1
    return ans


def linear_cost(a, target, mode):
    """Comparisons a plain left-to-right scan would need."""
    if mode == "last" or target not in a:
        return len(a)
    return a.index(target) + 1


def record_steps(a, target, mode="any"):
    n = len(a)
    lo, hi, ans, it = 0, n - 1, -1, 0
    # ln = which line of the code panel in the UI gets highlighted
    ln_lt, ln_gt, ln_end = (7, 9, 10) if mode == "any" else (8, 10, 11)
    steps = []

    def add(mid, ln, msg, c, done=None, res=None, keep=-1):
        steps.append({"lo": lo, "hi": hi, "mid": mid, "ans": keep if keep >= 0 else None,
                      "ln": ln, "c": c, "msg": msg, "done": done, "res": res})

    add(-1, 1, f"Looking for {target} in {n} sorted numbers. The window starts as the whole list: lo = 0, hi = {n - 1}.", 0)
    while lo <= hi:
        mid = (lo + hi) // 2
        v = a[mid]
        it += 1
        add(mid, 3, f"Window is index {lo} to {hi}. mid = ({lo} + {hi}) // 2 = {mid}, and a[{mid}] = {v}.", it - 1, keep=ans)
        if v == target:
            if mode == "any":
                add(mid, 5, f"{v} equals {target}. Found at index {mid}.", it, "ok", mid)
                return steps
            ans = mid
            if mode == "first":
                hi = mid - 1
                add(mid, 6, f"a[{mid}] = {target}, so ans = {mid}. An earlier copy could still be hiding on the left, so hi = {hi}.", it, keep=ans)
            else:
                lo = mid + 1
                add(mid, 6, f"a[{mid}] = {target}, so ans = {mid}. A later copy could still be hiding on the right, so lo = {lo}.", it, keep=ans)
        elif v < target:
            lo = mid + 1
            add(mid, ln_lt, f"{v} is smaller than {target}, so mid and everything left of it are out. lo = {lo}.", it, keep=ans)
        else:
            hi = mid - 1
            add(mid, ln_gt, f"{v} is bigger than {target}, so mid and everything right of it are out. hi = {hi}.", it, keep=ans)
    if ans >= 0:
        add(-1, ln_end, f"Window is empty. The {mode} {target} sits at index {ans}.", it, "ok", ans, keep=ans)
    else:
        add(-1, ln_end, f"Window is empty (lo = {lo}, hi = {hi}), so {target} is not in the list. It would slot in at index {lo}.", it, "bad", -1)
    return steps
