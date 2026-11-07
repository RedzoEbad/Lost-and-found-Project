"""
Merge sort, used to rank candidate matches from best to worst score.

Time: O(k log k) in every case.  Space: O(k).  Stable: yes
(reports with equal scores keep their original order).
"""


def merge_sort(items, key, descending=True):
    if len(items) <= 1:
        return list(items)

    mid = len(items) // 2
    left = merge_sort(items[:mid], key, descending)
    right = merge_sort(items[mid:], key, descending)
    return _merge(left, right, key, descending)


def _merge(left, right, key, descending):
    result = []
    i = j = 0
    while i < len(left) and j < len(right):
        a, b = key(left[i]), key(right[j])
        take_left = a >= b if descending else a <= b  # ">=" / "<=" keeps it stable
        if take_left:
            result.append(left[i])
            i += 1
        else:
            result.append(right[j])
            j += 1
    result.extend(left[i:])
    result.extend(right[j:])
    return result
