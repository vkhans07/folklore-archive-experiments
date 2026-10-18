"""One-to-one matching within a document, page, and label."""
from collections import Counter, defaultdict
import unicodedata


def normalized_text(value):
    return " ".join(unicodedata.normalize("NFC", value).split())


def edit_distance(a, b):
    a, b = normalized_text(a), normalized_text(b)
    previous = list(range(len(b) + 1))
    for i, ca in enumerate(a, 1):
        current = [i]
        for j, cb in enumerate(b, 1):
            current.append(min(current[-1] + 1, previous[j] + 1, previous[j - 1] + (ca != cb)))
        previous = current
    return previous[-1]


def iou(a, b):
    x0, y0 = max(a[0], b[0]), max(a[1], b[1])
    x1, y1 = min(a[2], b[2]), min(a[3], b[3])
    intersection = max(0, x1 - x0) * max(0, y1 - y0)
    area_a = (a[2] - a[0]) * (a[3] - a[1])
    area_b = (b[2] - b[0]) * (b[3] - b[1])
    return intersection / (area_a + area_b - intersection) if area_a + area_b > intersection else 0


def assignment_max(weights):
    """Hungarian assignment on a square matrix, maximizing sum of weights."""
    n = len(weights)
    if not n:
        return []
    max_w = max(max(row) for row in weights)
    cost = [[max_w - w for w in row] for row in weights]
    u, v = [0.0] * (n + 1), [0.0] * (n + 1)
    p, way = [0] * (n + 1), [0] * (n + 1)
    for i in range(1, n + 1):
        p[0] = i
        j0, minv, used = 0, [float("inf")] * (n + 1), [False] * (n + 1)
        while True:
            used[j0] = True
            i0, delta, j1 = p[j0], float("inf"), 0
            for j in range(1, n + 1):
                if not used[j]:
                    cur = cost[i0 - 1][j - 1] - u[i0] - v[j]
                    if cur < minv[j]:
                        minv[j], way[j] = cur, j0
                    if minv[j] < delta:
                        delta, j1 = minv[j], j
            for j in range(n + 1):
                if used[j]:
                    u[p[j]] += delta
                    v[j] -= delta
                else:
                    minv[j] -= delta
            j0 = j1
            if p[j0] == 0:
                break
        while True:
            j1 = way[j0]
            p[j0] = p[j1]
            j0 = j1
            if j0 == 0:
                break
    result = [None] * n
    for j in range(1, n + 1):
        result[p[j] - 1] = j - 1
    return result


def region_pairs(refs, preds, threshold=0.5):
    """Maximize qualified pair count first, then total IoU; no cross-page/label pairs."""
    groups = defaultdict(lambda: ([], []))
    for i, r in enumerate(refs):
        groups[(r["page_num"], r["label"])][0].append((i, r))
    for j, p in enumerate(preds):
        groups[(p["page_num"], p["label"])][1].append((j, p))
    pairs = []
    for ref_group, pred_group in groups.values():
        nr, np = len(ref_group), len(pred_group)
        if not nr or not np:
            continue
        n = nr + np
        bonus = n + 1  # Exceeds the largest possible total IoU difference.
        weights = [[0.0] * n for _ in range(n)]
        for i, (_, ref) in enumerate(ref_group):
            for j, (_, pred) in enumerate(pred_group):
                overlap = iou(ref["bbox"], pred["bbox"])
                weights[i][j] = bonus + overlap if overlap >= threshold else -1.0
        match = assignment_max(weights)
        for i in range(nr):
            j = match[i]
            if j < np:
                overlap = iou(ref_group[i][1]["bbox"], pred_group[j][1]["bbox"])
                if overlap >= threshold:
                    pairs.append((ref_group[i][0], pred_group[j][0], overlap))
    return pairs


def text_exact_count(refs, preds):
    """Multiset intersection by (page, label, NFC/whitespace-normalized text)."""
    key = lambda row: (row["page_num"], row["label"], normalized_text(row["text"]))
    a, b = Counter(map(key, refs)), Counter(map(key, preds))
    return sum((a & b).values())


def prf(tp, predicted, expected):
    precision = tp / predicted if predicted else (1.0 if not expected else 0.0)
    recall = tp / expected if expected else (1.0 if not predicted else 0.0)
    f1 = 2 * precision * recall / (precision + recall) if precision + recall else 0.0
    return precision, recall, f1
