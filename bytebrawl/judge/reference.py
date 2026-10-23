"""Reference solutions for the seeded problems.

Plain functions, no Django: the seed command runs them to generate
`expected_output`, and tests use them as known-good answers.
"""


def solve_two_sum(data):
    lines = data.strip().split('\n')
    _, target = map(int, lines[0].split())
    nums = list(map(int, lines[1].split()))
    seen = {}
    for i, value in enumerate(nums):
        if target - value in seen:
            return f'{seen[target - value]} {i}'
        seen[value] = i
    return '-1 -1'


def solve_valid_parentheses(data):
    pairs = {')': '(', ']': '[', '}': '{'}
    stack = []
    for char in data.strip():
        if char in '([{':
            stack.append(char)
        elif char in pairs and (not stack or stack.pop() != pairs[char]):
            return 'NO'
    return 'YES' if not stack else 'NO'


def solve_binary_search(data):
    lines = data.strip().split('\n')
    _, target = map(int, lines[0].split())
    nums = list(map(int, lines[1].split()))
    lo, hi = 0, len(nums) - 1
    while lo <= hi:
        mid = (lo + hi) // 2
        if nums[mid] == target:
            return str(mid)
        if nums[mid] < target:
            lo = mid + 1
        else:
            hi = mid - 1
    return '-1'


def solve_max_subarray(data):
    nums = list(map(int, data.strip().split('\n')[1].split()))
    best = current = nums[0]
    for value in nums[1:]:
        current = max(value, current + value)
        best = max(best, current)
    return str(best)


def solve_merge_intervals(data):
    lines = data.strip().split('\n')
    count = int(lines[0])
    intervals = sorted(tuple(map(int, lines[i + 1].split())) for i in range(count))
    merged = []
    for start, end in intervals:
        if merged and start <= merged[-1][1]:
            merged[-1][1] = max(merged[-1][1], end)
        else:
            merged.append([start, end])
    return '\n'.join(f'{s} {e}' for s, e in merged)


def solve_coin_change(data):
    lines = data.strip().split('\n')
    _, amount = map(int, lines[0].split())
    coins = list(map(int, lines[1].split()))
    unreachable = amount + 1
    best = [0] + [unreachable] * amount
    for target in range(1, amount + 1):
        for coin in coins:
            if coin <= target:
                best[target] = min(best[target], best[target - coin] + 1)
    return str(best[amount] if best[amount] != unreachable else -1)


def solve_num_islands(data):
    lines = data.strip().split('\n')
    rows, cols = map(int, lines[0].split())
    grid = [list(lines[r + 1]) for r in range(rows)]
    islands = 0

    for r in range(rows):
        for c in range(cols):
            if grid[r][c] != '1':
                continue
            islands += 1
            stack = [(r, c)]
            grid[r][c] = '0'
            while stack:
                cr, cc = stack.pop()
                for nr, nc in ((cr - 1, cc), (cr + 1, cc), (cr, cc - 1), (cr, cc + 1)):
                    if 0 <= nr < rows and 0 <= nc < cols and grid[nr][nc] == '1':
                        grid[nr][nc] = '0'
                        stack.append((nr, nc))
    return str(islands)


def solve_trapping_rain(data):
    heights = list(map(int, data.strip().split('\n')[1].split()))
    if not heights:
        return '0'
    left, right = 0, len(heights) - 1
    left_max, right_max, total = heights[left], heights[right], 0
    while left < right:
        if left_max <= right_max:
            left += 1
            left_max = max(left_max, heights[left])
            total += left_max - heights[left]
        else:
            right -= 1
            right_max = max(right_max, heights[right])
            total += right_max - heights[right]
    return str(total)


def solve_edit_distance(data):
    lines = data.strip().split('\n')
    a, b = lines[0], lines[1]
    previous = list(range(len(b) + 1))
    for i in range(1, len(a) + 1):
        current = [i] + [0] * len(b)
        for j in range(1, len(b) + 1):
            if a[i - 1] == b[j - 1]:
                current[j] = previous[j - 1]
            else:
                current[j] = 1 + min(previous[j - 1], previous[j], current[j - 1])
        previous = current
    return str(previous[len(b)])


def solve_longest_valid_parens(data):
    s = data.strip()
    best, stack = 0, [-1]
    for i, char in enumerate(s):
        if char == '(':
            stack.append(i)
        else:
            stack.pop()
            if not stack:
                stack.append(i)
            else:
                best = max(best, i - stack[-1])
    return str(best)
