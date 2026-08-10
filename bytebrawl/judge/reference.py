"""Seed the problem bank with fabricated problems and test cases.

Expected outputs are not hand-written. Each problem carries a reference solver,
and the command runs it over every input to produce `expected_output`. That means
the fixtures cannot drift out of sync with themselves, and a typo in an input
surfaces as a wrong-looking output rather than silently grading everyone wrong.

Idempotent: re-running upserts on q_no and rebuilds that problem's test cases.

    python manage.py seed_problems
    python manage.py seed_problems --clear
"""

from django.core.management.base import BaseCommand
from django.db import transaction

from problembank.models import Problems, TestCases


# ---------------------------------------------------------------- solvers
# Reference implementations. Used only to generate expected output at seed time.

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
        elif char in pairs:
            if not stack or stack.pop() != pairs[char]:
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


# ---------------------------------------------------------------- fixtures

PROBLEMS = [
    {
        'q_no': 1,
        'q_title': 'Two Sum',
        'q_tag': 'array',
        'q_difficulty': 'Easy',
        'q_description': (
            'Given an array of integers and a target value, find the two numbers '
            'that add up to the target and report their positions.\n\n'
            'Each input has exactly one solution, and you may not use the same '
            'element twice.'
        ),
        'q_input_format': (
            'Line 1: two integers n and target.\n'
            'Line 2: n space-separated integers.\n\n'
            'Constraints:\n'
            '  2 <= n <= 10^4\n'
            '  -10^9 <= each value, target <= 10^9'
        ),
        'q_output_format': (
            'Two 0-based indices in ascending order, separated by a space.'
        ),
        'solver': solve_two_sum,
        'inputs': [
            '4 9\n2 7 11 15',
            '3 6\n3 2 4',
            '2 6\n3 3',
            '5 -8\n-3 4 3 -5 -1',
            '6 20\n1 5 9 11 14 7',
            '4 0\n-5 5 3 9',
            '7 21\n1 3 6 10 15 21 28',
            '8 19\n2 4 6 8 10 12 14 17',
        ],
    },
    {
        'q_no': 2,
        'q_title': 'Valid Parentheses',
        'q_tag': 'stack',
        'q_difficulty': 'Easy',
        'q_description': (
            'Given a string containing only the characters ()[]{}, decide whether '
            'the brackets are balanced.\n\n'
            'Brackets must close in the correct order, and every opening bracket '
            'must be closed by one of the same type.'
        ),
        'q_input_format': (
            'A single line containing the bracket string.\n\n'
            'Constraints:\n'
            '  1 <= length <= 10^4\n'
            '  The string contains only the characters ()[]{}'
        ),
        'q_output_format': 'YES if the string is balanced, otherwise NO.',
        'solver': solve_valid_parentheses,
        'inputs': [
            '()',
            '()[]{}',
            '(]',
            '([)]',
            '{[]}',
            '(((',
            '((())())',
        ],
    },
    {
        'q_no': 3,
        'q_title': 'Binary Search',
        'q_tag': 'binary-search',
        'q_difficulty': 'Easy',
        'q_description': (
            'Given a sorted array of distinct integers and a target value, return '
            'the index of the target.\n\n'
            'If the target is not present, return -1. Your solution must run in '
            'O(log n) time.'
        ),
        'q_input_format': (
            'Line 1: two integers n and target.\n'
            'Line 2: n space-separated integers in strictly ascending order.\n\n'
            'Constraints:\n'
            '  1 <= n <= 10^4\n'
            '  -10^9 <= each value, target <= 10^9'
        ),
        'q_output_format': 'The 0-based index of the target, or -1 if absent.',
        'solver': solve_binary_search,
        'inputs': [
            '5 9\n1 3 5 7 9',
            '5 2\n1 3 5 7 9',
            '1 42\n42',
            '6 1\n1 2 3 4 5 6',
            '8 15\n2 4 6 8 10 12 14 16',
            '7 -3\n-9 -7 -5 -3 -1 0 4',
        ],
    },
    {
        'q_no': 4,
        'q_title': 'Maximum Subarray',
        'q_tag': 'dp',
        'q_difficulty': 'Medium',
        'q_description': (
            'Given an integer array, find the contiguous subarray with the largest '
            'sum and report that sum.\n\n'
            'The subarray must contain at least one element, so an all-negative '
            'array yields its largest single value.'
        ),
        'q_input_format': (
            'Line 1: an integer n.\n'
            'Line 2: n space-separated integers.\n\n'
            'Constraints:\n'
            '  1 <= n <= 10^5\n'
            '  -10^4 <= each value <= 10^4'
        ),
        'q_output_format': 'A single integer: the maximum subarray sum.',
        'solver': solve_max_subarray,
        'inputs': [
            '9\n-2 1 -3 4 -1 2 1 -5 4',
            '1\n1',
            '5\n5 4 -1 7 8',
            '4\n-1 -2 -3 -4',
            '6\n-2 -3 4 -1 -2 1',
            '3\n0 0 0',
            '7\n8 -19 5 -4 20 -1 3',
            '2\n-5 10',
        ],
    },
    {
        'q_no': 5,
        'q_title': 'Merge Intervals',
        'q_tag': 'sorting',
        'q_difficulty': 'Medium',
        'q_description': (
            'Given a collection of intervals, merge all overlapping ones and return '
            'the result in ascending order.\n\n'
            'Two intervals overlap if they share at least one point, so [1,4] and '
            '[4,5] merge into [1,5].'
        ),
        'q_input_format': (
            'Line 1: an integer n.\n'
            'Next n lines: two integers l and r describing one interval.\n\n'
            'Constraints:\n'
            '  1 <= n <= 10^4\n'
            '  0 <= l <= r <= 10^6'
        ),
        'q_output_format': (
            'One merged interval per line as "l r", sorted by start point.'
        ),
        'solver': solve_merge_intervals,
        'inputs': [
            '4\n1 3\n2 6\n8 10\n15 18',
            '2\n1 4\n4 5',
            '1\n5 7',
            '3\n1 10\n2 3\n4 5',
            '4\n5 6\n1 2\n3 4\n7 8',
            '3\n1 4\n0 4\n3 5',
            '5\n2 3\n4 5\n6 7\n8 9\n1 10',
        ],
    },
    {
        'q_no': 6,
        'q_title': 'Coin Change',
        'q_tag': 'dp',
        'q_difficulty': 'Medium',
        'q_description': (
            'Given coin denominations and a target amount, find the fewest coins '
            'needed to make that amount.\n\n'
            'You have an unlimited supply of each denomination. If the amount '
            'cannot be made, report -1.'
        ),
        'q_input_format': (
            'Line 1: two integers n and amount.\n'
            'Line 2: n space-separated coin denominations.\n\n'
            'Constraints:\n'
            '  1 <= n <= 12\n'
            '  0 <= amount <= 10^4\n'
            '  1 <= each denomination <= 2^31 - 1'
        ),
        'q_output_format': (
            'A single integer: the fewest coins needed, or -1 if impossible.'
        ),
        'solver': solve_coin_change,
        'inputs': [
            '3 11\n1 2 5',
            '1 3\n2',
            '1 0\n1',
            '4 63\n1 5 10 25',
            '2 7\n3 5',
            '3 30\n1 7 12',
            '2 6\n1 3',
            '3 100\n1 20 50',
            '4 27\n1 2 5 10',
        ],
    },
    {
        'q_no': 7,
        'q_title': 'Number of Islands',
        'q_tag': 'graph',
        'q_difficulty': 'Medium',
        'q_description': (
            'Given a grid of 1s (land) and 0s (water), count the number of islands.\n\n'
            'An island is a group of 1s connected horizontally or vertically. '
            'Diagonal contact does not connect two cells.'
        ),
        'q_input_format': (
            'Line 1: two integers rows and cols.\n'
            'Next rows lines: a string of cols characters, each 0 or 1.\n\n'
            'Constraints:\n'
            '  1 <= rows, cols <= 300'
        ),
        'q_output_format': 'A single integer: the number of islands.',
        'solver': solve_num_islands,
        'inputs': [
            '4 5\n11000\n11000\n00100\n00011',
            '1 1\n0',
            '1 1\n1',
            '3 3\n111\n111\n111',
            '3 3\n101\n010\n101',
            '4 4\n1001\n0110\n0110\n1001',
        ],
    },
    {
        'q_no': 8,
        'q_title': 'Trapping Rain Water',
        'q_tag': 'two-pointers',
        'q_difficulty': 'Hard',
        'q_description': (
            'Given an elevation map where each bar has width 1, compute how much '
            'water it traps after raining.\n\n'
            'Water sits above a position up to the lower of the highest bars to its '
            'left and right.'
        ),
        'q_input_format': (
            'Line 1: an integer n.\n'
            'Line 2: n space-separated non-negative integers.\n\n'
            'Constraints:\n'
            '  1 <= n <= 2 * 10^4\n'
            '  0 <= each height <= 10^5'
        ),
        'q_output_format': 'A single integer: the units of trapped water.',
        'solver': solve_trapping_rain,
        'inputs': [
            '12\n0 1 0 2 1 0 1 3 2 1 2 1',
            '6\n4 2 0 3 2 5',
            '3\n1 2 3',
            '1\n5',
            '5\n5 4 3 2 1',
            '5\n3 0 0 0 3',
            '7\n0 0 0 0 0 0 0',
            '9\n2 0 2 0 2 0 2 0 2',
        ],
    },
    {
        'q_no': 9,
        'q_title': 'Edit Distance',
        'q_tag': 'dp',
        'q_difficulty': 'Hard',
        'q_description': (
            'Given two words, find the minimum number of single-character edits '
            'needed to turn the first into the second.\n\n'
            'The permitted operations are insert, delete, and replace.'
        ),
        'q_input_format': (
            'Line 1: the first word.\n'
            'Line 2: the second word.\n\n'
            'Constraints:\n'
            '  1 <= length of each word <= 500\n'
            '  Both words consist of lowercase English letters'
        ),
        'q_output_format': 'A single integer: the minimum number of operations.',
        'solver': solve_edit_distance,
        'inputs': [
            'horse\nros',
            'intention\nexecution',
            'abc\nabc',
            'a\nb',
            'kitten\nsitting',
            'flaw\nlawn',
            'sunday\nsaturday',
        ],
    },
    {
        'q_no': 10,
        'q_title': 'Longest Valid Parentheses',
        'q_tag': 'stack',
        'q_difficulty': 'Hard',
        'q_description': (
            'Given a string of only ( and ), find the length of the longest '
            'substring that forms well-formed parentheses.\n\n'
            'The substring must be contiguous, and every bracket in it must be '
            'correctly matched.'
        ),
        'q_input_format': (
            'A single line containing only the characters ( and ).\n\n'
            'Constraints:\n'
            '  1 <= length <= 3 * 10^4'
        ),
        'q_output_format': (
            'A single integer: the length of the longest valid substring.'
        ),
        'solver': solve_longest_valid_parens,
        'inputs': [
            '(()',
            ')()())',
            '()(())',
            '((((',
            '))))',
            '()(()',
            '(()())',
        ],
    },
]

# The first two cases of every problem are shown to the user; the rest are hidden.
PUBLIC_CASES = 2


class Command(BaseCommand):
    help = 'Seed the problem bank with fabricated problems and generated test cases.'

    def add_arguments(self, parser):
        parser.add_argument(
            '--clear',
            action='store_true',
            help='Delete every existing problem before seeding.',
        )

    @transaction.atomic
    def handle(self, *args, **options):
        if options['clear']:
            deleted, _ = Problems.objects.all().delete()
            self.stdout.write(self.style.WARNING(f'Cleared {deleted} row(s).'))

        totals = {'problems': 0, 'cases': 0}

        for spec in PROBLEMS:
            solver = spec['solver']
            inputs = spec['inputs']

            sample_input = inputs[0]
            sample_output = solver(sample_input)

            problem, created = Problems.objects.update_or_create(
                q_no=spec['q_no'],
                defaults={
                    'q_title': spec['q_title'],
                    'q_description': spec['q_description'],
                    'q_input_format': spec['q_input_format'],
                    'q_output_format': spec['q_output_format'],
                    'q_sample_io': f'Input:\n{sample_input}\n\nOutput:\n{sample_output}',
                    'q_tag': spec['q_tag'],
                    'q_difficulty': spec['q_difficulty'],
                },
            )

            # Rebuild rather than append, so re-running doesn't duplicate.
            TestCases.objects.filter(q_id=problem).delete()

            TestCases.objects.bulk_create([
                TestCases(
                    q_id=problem,
                    test_case_no=index,
                    visiblity='PUBLIC' if index <= PUBLIC_CASES else 'PRIVATE',
                    test_case=raw_input,
                    expected_output=solver(raw_input),
                )
                for index, raw_input in enumerate(inputs, start=1)
            ])

            totals['problems'] += 1
            totals['cases'] += len(inputs)

            verb = 'created' if created else 'updated'
            self.stdout.write(
                f'  {spec["q_no"]:>2}. {spec["q_title"]:<28} '
                f'{spec["q_difficulty"]:<7} {len(inputs)} cases  ({verb})'
            )

        self.stdout.write(self.style.SUCCESS(
            f'\nSeeded {totals["problems"]} problems and {totals["cases"]} test cases.'
        ))