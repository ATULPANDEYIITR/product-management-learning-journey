"""
GREATEST COMMON DIVISOR (GCD)
=============================

A comprehensive, executable study guide covering the Greatest Common Divisor
from absolute beginner concepts through advanced algorithms, implementation
details, edge cases, performance analysis, and practical applications.

The script uses only Python's standard library.

Run:
    python gcd_complete_guide.py
"""

from __future__ import annotations

from math import gcd as math_gcd
from functools import reduce
from time import perf_counter
from typing import Iterable, Sequence


# =============================================================================
# 1. FUNDAMENTAL IDEA
# =============================================================================

def explain_gcd() -> None:
    """
    The Greatest Common Divisor of two integers is the largest positive integer
    that divides both integers exactly.

    Example:
        Divisors of 12 = 1, 2, 3, 4, 6, 12
        Divisors of 18 = 1, 2, 3, 6, 9, 18

        Common divisors = 1, 2, 3, 6
        Therefore gcd(12, 18) = 6

    A divisor d of n satisfies:
        n % d == 0
    """
    print("\n" + "=" * 78)
    print("1. FUNDAMENTAL IDEA")
    print("=" * 78)

    a, b = 12, 18

    divisors_a = [d for d in range(1, abs(a) + 1) if a % d == 0]
    divisors_b = [d for d in range(1, abs(b) + 1) if b % d == 0]
    common = sorted(set(divisors_a) & set(divisors_b))

    print(f"Number A: {a}")
    print(f"Number B: {b}")
    print(f"Divisors of {a}: {divisors_a}")
    print(f"Divisors of {b}: {divisors_b}")
    print(f"Common divisors: {common}")
    print(f"GCD: {common[-1]}")


# =============================================================================
# 2. TERMINOLOGY AND BASIC DEFINITIONS
# =============================================================================

def terminology_demo() -> None:
    """
    Important terminology:

    Divisor:
        A number that divides another number without remainder.

    Multiple:
        A number obtained by multiplying an integer by another integer.

    Common divisor:
        A divisor shared by two or more integers.

    Greatest common divisor:
        The largest positive common divisor.

    Coprime numbers:
        Two integers whose GCD is 1.

    Relatively prime:
        Another term for coprime.

    GCD is also called HCF (Highest Common Factor).
    """
    print("\n" + "=" * 78)
    print("2. TERMINOLOGY")
    print("=" * 78)

    examples = [
        (8, 12),
        (14, 25),
        (21, 35),
    ]

    for a, b in examples:
        result = math_gcd(a, b)
        relationship = "coprime" if result == 1 else "not coprime"
        print(f"gcd({a}, {b}) = {result} -> {relationship}")


# =============================================================================
# 3. NAIVE / BRUTE-FORCE METHOD
# =============================================================================

def gcd_brute_force(a: int, b: int) -> int:
    """
    Compute GCD by testing every possible positive divisor.

    This implementation demonstrates the definition directly.

    Time complexity:
        O(min(|a|, |b|))

    Space complexity:
        O(1)

    It is educational but inefficient for large integers.
    """
    a = abs(a)
    b = abs(b)

    if a == 0:
        return b
    if b == 0:
        return a

    greatest = 1

    for candidate in range(1, min(a, b) + 1):
        if a % candidate == 0 and b % candidate == 0:
            greatest = candidate

    return greatest


def demonstrate_brute_force() -> None:
    print("\n" + "=" * 78)
    print("3. BRUTE-FORCE GCD")
    print("=" * 78)

    pairs = [(12, 18), (48, 180), (17, 29), (0, 15)]

    for a, b in pairs:
        print(
            f"gcd_brute_force({a}, {b}) = "
            f"{gcd_brute_force(a, b)}"
        )


# =============================================================================
# 4. EUCLIDEAN ALGORITHM
# =============================================================================

def gcd_euclidean(a: int, b: int) -> int:
    """
    Compute GCD using the Euclidean algorithm.

    Fundamental identity:

        gcd(a, b) = gcd(b, a % b)

    repeatedly until the second value becomes zero.

    Example:

        gcd(48, 18)
        = gcd(18, 48 % 18)
        = gcd(18, 12)
        = gcd(12, 6)
        = gcd(6, 0)
        = 6

    Time complexity:
        O(log(min(|a|, |b|)))

    Space complexity:
        O(1)

    Python's modulo operation handles the arithmetic safely for arbitrary-size
    integers. Converting inputs to absolute values gives a non-negative GCD.
    """
    a = abs(a)
    b = abs(b)

    while b != 0:
        a, b = b, a % b

    return a


def explain_euclidean_steps(a: int, b: int) -> None:
    """Print every remainder step of the Euclidean algorithm."""
    print(f"\nEuclidean algorithm for gcd({a}, {b}):")

    a, b = abs(a), abs(b)

    if a == 0 and b == 0:
        print("Both values are zero; the conventional Python result is 0.")
        return

    while b != 0:
        quotient, remainder = divmod(a, b)
        print(f"{a} = {b} × {quotient} + {remainder}")
        a, b = b, remainder

    print(f"GCD = {a}")


def demonstrate_euclidean_algorithm() -> None:
    print("\n" + "=" * 78)
    print("4. EUCLIDEAN ALGORITHM")
    print("=" * 78)

    explain_euclidean_steps(48, 18)
    explain_euclidean_steps(252, 105)
    explain_euclidean_steps(1071, 462)


# =============================================================================
# 5. RECURSIVE EUCLIDEAN ALGORITHM
# =============================================================================

def gcd_recursive(a: int, b: int) -> int:
    """
    Recursive form of the Euclidean algorithm.

    Mathematical recurrence:

        gcd(a, 0) = |a|
        gcd(a, b) = gcd(b, a mod b)

    Recursion depth is O(log(min(|a|, |b|))) for positive inputs, so ordinary
    Euclidean recursion is typically shallow. An iterative implementation is
    still preferable when eliminating recursion is a design goal.
    """
    a = abs(a)
    b = abs(b)

    if b == 0:
        return a

    return gcd_recursive(b, a % b)


def demonstrate_recursive_gcd() -> None:
    print("\n" + "=" * 78)
    print("5. RECURSIVE EUCLIDEAN ALGORITHM")
    print("=" * 78)

    for a, b in [(48, 18), (270, 192), (100, 35)]:
        print(f"gcd_recursive({a}, {b}) = {gcd_recursive(a, b)}")


# =============================================================================
# 6. WHY THE EUCLIDEAN IDENTITY WORKS
# =============================================================================

def prove_euclidean_identity(a: int, b: int) -> None:
    """
    Demonstrate the reasoning behind:

        gcd(a, b) = gcd(b, a % b)

    Suppose:
        a = bq + r

    Any common divisor d of a and b divides:

        a - bq = r

    Therefore every common divisor of a and b is also a common divisor of
    b and r.

    Conversely, if d divides b and r, then:

        bq + r = a

    so d also divides a.

    The two pairs therefore have exactly the same common divisors.
    """
    print("\n" + "=" * 78)
    print("6. WHY THE EUCLIDEAN ALGORITHM WORKS")
    print("=" * 78)

    a, b = abs(a), abs(b)

    if b == 0:
        print(f"gcd({a}, 0) = {a}")
        return

    q, r = divmod(a, b)

    print(f"a = {a}")
    print(f"b = {b}")
    print(f"a = b × q + r")
    print(f"{a} = {b} × {q} + {r}")
    print(f"gcd({a}, {b}) = gcd({b}, {r})")
    print(f"Result = {gcd_euclidean(a, b)}")


# =============================================================================
# 7. GCD WITH NEGATIVE NUMBERS AND ZERO
# =============================================================================

def demonstrate_edge_cases() -> None:
    print("\n" + "=" * 78)
    print("7. EDGE CASES")
    print("=" * 78)

    cases = [
        (0, 0),
        (0, 12),
        (12, 0),
        (-12, 18),
        (12, -18),
        (-12, -18),
        (1, 999),
        (999, 1),
    ]

    for a, b in cases:
        print(f"gcd({a}, {b}) = {gcd_euclidean(a, b)}")

    print("\nImportant convention:")
    print("gcd(0, n) = |n|")
    print("gcd(0, 0) = 0 in Python's math.gcd convention.")
    print("The mathematical treatment of gcd(0, 0) is convention-dependent.")


# =============================================================================
# 8. COPRIME NUMBERS
# =============================================================================

def are_coprime(a: int, b: int) -> bool:
    """Return True exactly when the two integers have GCD equal to 1."""
    return gcd_euclidean(a, b) == 1


def demonstrate_coprime_numbers() -> None:
    print("\n" + "=" * 78)
    print("8. COPRIME NUMBERS")
    print("=" * 78)

    for a, b in [(8, 15), (14, 21), (35, 64), (17, 68)]:
        print(f"{a} and {b}: coprime = {are_coprime(a, b)}")


# =============================================================================
# 9. GCD OF MORE THAN TWO NUMBERS
# =============================================================================

def gcd_many(numbers: Iterable[int]) -> int:
    """
    Compute the GCD of an arbitrary iterable.

    Property:

        gcd(a, b, c) = gcd(gcd(a, b), c)

    Therefore GCD is associative and can be reduced pair by pair.

    Empty input returns 0, matching the identity convention used by
    math.gcd(*values).
    """
    return reduce(gcd_euclidean, numbers, 0)


def demonstrate_gcd_many() -> None:
    print("\n" + "=" * 78)
    print("9. GCD OF MANY NUMBERS")
    print("=" * 78)

    examples = [
        [24, 36, 60],
        [100, 250, 400],
        [17, 19, 23],
        [0, 12, 24],
        [],
    ]

    for values in examples:
        print(f"gcd_many({values}) = {gcd_many(values)}")


# =============================================================================
# 10. GCD OF A LIST USING DIFFERENT APPROACHES
# =============================================================================

def gcd_many_loop(numbers: Sequence[int]) -> int:
    """Iterative reduction without functools.reduce."""
    result = 0

    for number in numbers:
        result = gcd_euclidean(result, number)

    return result


def gcd_many_math(numbers: Sequence[int]) -> int:
    """Use Python's optimized standard-library implementation."""
    return math_gcd(*numbers)


def demonstrate_multiple_number_methods() -> None:
    print("\n" + "=" * 78)
    print("10. MULTIPLE-NUMBER IMPLEMENTATIONS")
    print("=" * 78)

    values = [84, 126, 210, 294]

    print("Input:", values)
    print("Loop:", gcd_many_loop(values))
    print("reduce:", gcd_many(values))
    print("math.gcd:", gcd_many_math(values))


# =============================================================================
# 11. GCD AND LCM RELATIONSHIP
# =============================================================================

def lcm_using_gcd(a: int, b: int) -> int:
    """
    Compute Least Common Multiple using GCD.

    For non-zero integers:

        lcm(a, b) = |a * b| / gcd(a, b)

    To reduce the size of intermediate multiplication, use:

        abs(a // gcd(a, b) * b)

    instead of:

        abs(a * b) // gcd(a, b)

    Python integers do not overflow like fixed-width machine integers, but the
    reduced-intermediate form is still a useful algorithmic pattern.
    """
    a = abs(a)
    b = abs(b)

    if a == 0 or b == 0:
        return 0

    return abs((a // gcd_euclidean(a, b)) * b)


def demonstrate_gcd_lcm() -> None:
    print("\n" + "=" * 78)
    print("11. GCD AND LCM")
    print("=" * 78)

    pairs = [(12, 18), (8, 20), (21, 28)]

    for a, b in pairs:
        g = gcd_euclidean(a, b)
        l = lcm_using_gcd(a, b)

        print(f"a = {a}, b = {b}")
        print(f"GCD = {g}")
        print(f"LCM = {l}")
        print(f"GCD × LCM = {g * l}")
        print(f"|a × b| = {abs(a * b)}")
        print()


# =============================================================================
# 12. FRACTION REDUCTION
# =============================================================================

def reduce_fraction(numerator: int, denominator: int) -> tuple[int, int]:
    """
    Reduce a fraction to lowest terms.

    Example:
        84/126 -> 2/3

    The denominator cannot be zero.

    The sign is normalized so that the denominator is positive.
    """
    if denominator == 0:
        raise ValueError("Denominator cannot be zero.")

    if numerator == 0:
        return 0, 1

    divisor = gcd_euclidean(numerator, denominator)

    numerator //= divisor
    denominator //= divisor

    if denominator < 0:
        numerator = -numerator
        denominator = -denominator

    return numerator, denominator


def demonstrate_fraction_reduction() -> None:
    print("\n" + "=" * 78)
    print("12. FRACTION REDUCTION")
    print("=" * 78)

    fractions = [
        (84, 126),
        (-45, 60),
        (45, -60),
        (-45, -60),
        (0, 25),
    ]

    for numerator, denominator in fractions:
        reduced = reduce_fraction(numerator, denominator)
        print(f"{numerator}/{denominator} -> {reduced[0]}/{reduced[1]}")

    try:
        reduce_fraction(5, 0)
    except ValueError as error:
        print("5/0 -> error:", error)


# =============================================================================
# 13. GCD OF DECIMAL-LIKE VALUES: WHY DIRECT FLOAT GCD IS WRONG
# =============================================================================

def demonstrate_float_warning() -> None:
    """
    GCD is fundamentally an integer divisibility concept.

    Floating-point values can represent decimal quantities approximately, so
    applying integer GCD logic directly to arbitrary floats is inappropriate.

    If decimal values have a known fixed precision, scale them to integers
    before applying GCD.

    Example:
        1.20 and 1.80
        scale by 100:
        120 and 180
        gcd = 60
        therefore common exact unit = 0.60
    """
    print("\n" + "=" * 78)
    print("13. DECIMAL VALUES AND INTEGER SCALING")
    print("=" * 78)

    amount_a = 1.20
    amount_b = 1.80

    scale = 100
    integer_a = round(amount_a * scale)
    integer_b = round(amount_b * scale)

    integer_gcd = gcd_euclidean(integer_a, integer_b)
    decimal_gcd = integer_gcd / scale

    print(f"{amount_a} and {amount_b}")
    print(f"Scaled integers: {integer_a}, {integer_b}")
    print(f"Integer GCD: {integer_gcd}")
    print(f"Represented common unit: {decimal_gcd}")


# =============================================================================
# 14. GCD AND LINEAR COMBINATIONS
# =============================================================================

def bezout_demo(a: int, b: int) -> tuple[int, int, int]:
    """
    Extended Euclidean algorithm.

    Returns:
        (g, x, y)

    such that:

        ax + by = g

    where:

        g = gcd(a, b)

    This is Bézout's identity.

    The extended algorithm is important in modular arithmetic, modular
    inverses, Diophantine equations, and cryptographic algorithms.
    """
    original_a, original_b = a, b

    old_r, r = a, b
    old_s, s = 1, 0
    old_t, t = 0, 1

    while r != 0:
        quotient = old_r // r

        old_r, r = r, old_r - quotient * r
        old_s, s = s, old_s - quotient * s
        old_t, t = t, old_t - quotient * t

    # Normalize GCD to positive form.
    if old_r < 0:
        old_r = -old_r
        old_s = -old_s
        old_t = -old_t

    print(
        f"{original_a} × ({old_s}) + "
        f"{original_b} × ({old_t}) = {old_r}"
    )

    return old_r, old_s, old_t


def extended_gcd(a: int, b: int) -> tuple[int, int, int]:
    """
    Extended Euclidean algorithm without printing.

    Returns positive gcd whenever at least one input is non-zero.
    """
    old_r, r = a, b
    old_x, x = 1, 0
    old_y, y = 0, 1

    while r != 0:
        q = old_r // r

        old_r, r = r, old_r - q * r
        old_x, x = x, old_x - q * x
        old_y, y = y, old_y - q * y

    if old_r < 0:
        return -old_r, -old_x, -old_y

    return old_r, old_x, old_y


def demonstrate_bezout() -> None:
    print("\n" + "=" * 78)
    print("14. BÉZOUT'S IDENTITY AND EXTENDED EUCLIDEAN ALGORITHM")
    print("=" * 78)

    a, b = 240, 46
    g, x, y = extended_gcd(a, b)

    print(f"a = {a}")
    print(f"b = {b}")
    print(f"gcd = {g}")
    print(f"x = {x}")
    print(f"y = {y}")
    print(f"Verification: {a}*{x} + {b}*{y} = {a*x + b*y}")

    print("\nPrinted demonstration:")
    bezout_demo(240, 46)


# =============================================================================
# 15. MODULAR MULTIPLICATIVE INVERSE
# =============================================================================

def modular_inverse(a: int, modulus: int) -> int:
    """
    Find x such that:

        a*x ≡ 1 (mod modulus)

    A modular inverse exists exactly when:

        gcd(a, modulus) = 1

    The extended Euclidean algorithm supplies Bézout coefficients:

        ax + modulus*y = 1

    Therefore x is an inverse modulo modulus.
    """
    if modulus <= 0:
        raise ValueError("Modulus must be positive.")

    g, x, _ = extended_gcd(a, modulus)

    if g != 1:
        raise ValueError(
            f"No modular inverse exists because gcd({a}, {modulus}) = {g}."
        )

    return x % modulus


def demonstrate_modular_inverse() -> None:
    print("\n" + "=" * 78)
    print("15. MODULAR MULTIPLICATIVE INVERSE")
    print("=" * 78)

    a, modulus = 3, 11
    inverse = modular_inverse(a, modulus)

    print(f"Inverse of {a} modulo {modulus}: {inverse}")
    print(f"Verification: ({a} * {inverse}) % {modulus} = "
          f"{(a * inverse) % modulus}")

    try:
        modular_inverse(6, 15)
    except ValueError as error:
        print("6 modulo 15:", error)


# =============================================================================
# 16. LINEAR DIOPHANTINE EQUATIONS
# =============================================================================

def solve_linear_diophantine(
    a: int,
    b: int,
    c: int,
) -> tuple[int, int, int] | None:
    """
    Solve:

        ax + by = c

    A solution exists exactly when:

        gcd(a, b) divides c.

    Returns one solution (x, y, g), where g = gcd(a, b), or None.
    """
    g, x0, y0 = extended_gcd(a, b)

    if c % g != 0:
        return None

    multiplier = c // g

    return x0 * multiplier, y0 * multiplier, g


def demonstrate_diophantine_equation() -> None:
    print("\n" + "=" * 78)
    print("16. LINEAR DIOPHANTINE EQUATIONS")
    print("=" * 78)

    examples = [
        (15, 25, 5),
        (15, 25, 7),
        (21, 14, 35),
    ]

    for a, b, c in examples:
        result = solve_linear_diophantine(a, b, c)

        if result is None:
            print(f"{a}x + {b}y = {c}: no integer solution")
        else:
            x, y, g = result
            print(
                f"{a}x + {b}y = {c}: "
                f"x = {x}, y = {y}, gcd = {g}, "
                f"check = {a*x + b*y}"
            )


# =============================================================================
# 17. ALL DIVISORS FROM A GCD
# =============================================================================

def divisors(n: int) -> list[int]:
    """
    Return all positive divisors of |n|.

    Uses the square-root pairing property.

    If d divides n, then n/d also divides n.

    Time complexity:
        O(sqrt(n))

    Space complexity:
        O(number of divisors)
    """
    n = abs(n)

    if n == 0:
        raise ValueError("Zero has infinitely many integer divisors.")

    result: list[int] = []

    candidate = 1

    while candidate * candidate <= n:
        if n % candidate == 0:
            result.append(candidate)

            paired = n // candidate
            if paired != candidate:
                result.append(paired)

        candidate += 1

    return sorted(result)


def common_divisors_using_gcd(a: int, b: int) -> list[int]:
    """
    Every common divisor of a and b is a divisor of gcd(a, b).

    Therefore, instead of scanning both numbers, compute their GCD and list
    the divisors of that GCD.
    """
    g = gcd_euclidean(a, b)

    if g == 0:
        return []

    return divisors(g)


def demonstrate_common_divisors() -> None:
    print("\n" + "=" * 78)
    print("17. COMMON DIVISORS THROUGH THE GCD")
    print("=" * 78)

    a, b = 84, 126
    g = gcd_euclidean(a, b)

    print(f"gcd({a}, {b}) = {g}")
    print(f"All common divisors = {common_divisors_using_gcd(a, b)}")


# =============================================================================
# 18. GCD OF POLYNOMIAL-LIKE INTEGER COEFFICIENTS
# =============================================================================

def gcd_of_coefficients(coefficients: Iterable[int]) -> int:
    """
    Compute the GCD of polynomial coefficients.

    Example:

        12x^3 + 18x^2 + 30x

    has coefficient GCD:

        gcd(12, 18, 30) = 6

    The function operates only on integer coefficients and does not attempt
    symbolic polynomial division.
    """
    return gcd_many(coefficients)


def demonstrate_coefficient_gcd() -> None:
    print("\n" + "=" * 78)
    print("18. GCD OF INTEGER COEFFICIENTS")
    print("=" * 78)

    coefficients = [12, 18, 30]
    print(f"Coefficients: {coefficients}")
    print(f"Content GCD: {gcd_of_coefficients(coefficients)}")


# =============================================================================
# 19. GCD OF ARRAYS AND RANGE QUERIES
# =============================================================================

class GCDSegmentTree:
    """
    Segment tree supporting:

        1. Building from an integer array.
        2. Point updates.
        3. Range GCD queries.

    For a static array, prefix/suffix structures or sparse tables may be used
    depending on the query requirements. A segment tree is useful when values
    can change.

    Query complexity:
        O(log n)

    Point update:
        O(log n)

    Build:
        O(n)

    Memory:
        O(n)
    """

    def __init__(self, values: Sequence[int]):
        if not values:
            raise ValueError("Segment tree requires a non-empty sequence.")

        self.n = len(values)
        self.tree = [0] * (4 * self.n)
        self._build(values, 1, 0, self.n - 1)

    def _build(
        self,
        values: Sequence[int],
        node: int,
        left: int,
        right: int,
    ) -> None:
        if left == right:
            self.tree[node] = abs(values[left])
            return

        middle = (left + right) // 2

        self._build(values, node * 2, left, middle)
        self._build(values, node * 2 + 1, middle + 1, right)

        self.tree[node] = gcd_euclidean(
            self.tree[node * 2],
            self.tree[node * 2 + 1],
        )

    def query(self, query_left: int, query_right: int) -> int:
        """Return GCD of the inclusive range [query_left, query_right]."""
        if not 0 <= query_left <= query_right < self.n:
            raise IndexError("Invalid query range.")

        return self._query(
            1,
            0,
            self.n - 1,
            query_left,
            query_right,
        )

    def _query(
        self,
        node: int,
        left: int,
        right: int,
        query_left: int,
        query_right: int,
    ) -> int:
        if query_left <= left and right <= query_right:
            return self.tree[node]

        middle = (left + right) // 2

        if query_right <= middle:
            return self._query(
                node * 2,
                left,
                middle,
                query_left,
                query_right,
            )

        if query_left > middle:
            return self._query(
                node * 2 + 1,
                middle + 1,
                right,
                query_left,
                query_right,
            )

        left_gcd = self._query(
            node * 2,
            left,
            middle,
            query_left,
            query_right,
        )
        right_gcd = self._query(
            node * 2 + 1,
            middle + 1,
            right,
            query_left,
            query_right,
        )

        return gcd_euclidean(left_gcd, right_gcd)

    def update(self, index: int, value: int) -> None:
        """Replace one array element and update affected tree nodes."""
        if not 0 <= index < self.n:
            raise IndexError("Index out of range.")

        self._update(1, 0, self.n - 1, index, abs(value))

    def _update(
        self,
        node: int,
        left: int,
        right: int,
        index: int,
        value: int,
    ) -> None:
        if left == right:
            self.tree[node] = value
            return

        middle = (left + right) // 2

        if index <= middle:
            self._update(node * 2, left, middle, index, value)
        else:
            self._update(node * 2 + 1, middle + 1, right, index, value)

        self.tree[node] = gcd_euclidean(
            self.tree[node * 2],
            self.tree[node * 2 + 1],
        )


def demonstrate_segment_tree() -> None:
    print("\n" + "=" * 78)
    print("19. RANGE GCD WITH A SEGMENT TREE")
    print("=" * 78)

    values = [24, 36, 48, 60, 72, 90]
    tree = GCDSegmentTree(values)

    print("Array:", values)
    print("GCD [0, 2]:", tree.query(0, 2))
    print("GCD [1, 4]:", tree.query(1, 4))
    print("GCD [2, 5]:", tree.query(2, 5))

    tree.update(2, 54)

    print("\nAfter updating index 2 from 48 to 54:")
    print("GCD [0, 2]:", tree.query(0, 2))


# =============================================================================
# 20. GCD PREFIX TECHNIQUE
# =============================================================================

def gcd_prefix(values: Sequence[int]) -> list[int]:
    """
    prefix[i] = GCD of values[0:i+1].

    Useful when many queries ask for GCDs of prefixes.
    """
    result: list[int] = []
    current = 0

    for value in values:
        current = gcd_euclidean(current, value)
        result.append(current)

    return result


def demonstrate_prefix_gcd() -> None:
    print("\n" + "=" * 78)
    print("20. PREFIX GCD")
    print("=" * 78)

    values = [48, 72, 96, 120, 150]
    print("Values:", values)
    print("Prefix GCD:", gcd_prefix(values))


# =============================================================================
# 21. GCD AND PRIME FACTORIZATION
# =============================================================================

def prime_factorization(n: int) -> dict[int, int]:
    """
    Return the prime factorization of |n|.

    Example:
        360 = 2^3 × 3^2 × 5

    This function is intentionally simple and educational.

    Trial division is not appropriate for very large prime numbers because
    it can require O(sqrt(n)) trial candidates.
    """
    n = abs(n)

    if n < 2:
        return {}

    factors: dict[int, int] = {}

    while n % 2 == 0:
        factors[2] = factors.get(2, 0) + 1
        n //= 2

    factor = 3

    while factor * factor <= n:
        while n % factor == 0:
            factors[factor] = factors.get(factor, 0) + 1
            n //= factor

        factor += 2

    if n > 1:
        factors[n] = factors.get(n, 0) + 1

    return factors


def gcd_from_prime_factors(a: int, b: int) -> int:
    """
    Compute GCD from prime factorizations.

    If:

        a = product(p_i ^ alpha_i)
        b = product(p_i ^ beta_i)

    then:

        gcd(a, b) = product(p_i ^ min(alpha_i, beta_i))
    """
    factors_a = prime_factorization(a)
    factors_b = prime_factorization(b)

    result = 1

    for prime in factors_a.keys() & factors_b.keys():
        result *= prime ** min(factors_a[prime], factors_b[prime])

    return result


def demonstrate_prime_factorization_relationship() -> None:
    print("\n" + "=" * 78)
    print("21. GCD THROUGH PRIME FACTORIZATION")
    print("=" * 78)

    a, b = 360, 504

    print(f"{a} factors:", prime_factorization(a))
    print(f"{b} factors:", prime_factorization(b))
    print("GCD from factors:", gcd_from_prime_factors(a, b))
    print("Euclidean GCD:", gcd_euclidean(a, b))


# =============================================================================
# 22. GCD PROPERTY CHECKS
# =============================================================================

def verify_gcd_properties(a: int, b: int) -> None:
    """
    Demonstrate important algebraic properties.

    Commutativity:
        gcd(a, b) = gcd(b, a)

    Identity:
        gcd(a, 0) = |a|

    Divisibility:
        gcd(a, b) divides both a and b.

    Euclidean reduction:
        gcd(a, b) = gcd(b, a % b)

    Scaling:
        gcd(ka, kb) = |k| gcd(a, b)
    """
    g = gcd_euclidean(a, b)

    print("\n" + "=" * 78)
    print("22. GCD PROPERTIES")
    print("=" * 78)

    print("Commutativity:", g == gcd_euclidean(b, a))
    print("Divides a:", a % g == 0 if g else True)
    print("Divides b:", b % g == 0 if g else True)

    if b != 0:
        print(
            "Euclidean identity:",
            g == gcd_euclidean(b, a % b),
        )

    k = 7
    scaled_left = gcd_euclidean(k * a, k * b)
    scaled_right = abs(k) * g

    print("Scaling property:", scaled_left == scaled_right)


# =============================================================================
# 23. ADVANCED: BINARY GCD / STEIN'S ALGORITHM
# =============================================================================

def binary_gcd(a: int, b: int) -> int:
    """
    Compute GCD using Stein's binary GCD algorithm.

    It avoids general modulo operations by exploiting powers of two and
    subtraction.

    Rules:

        gcd(0, b) = |b|

        If both numbers are even:
            gcd(a, b) = 2 * gcd(a/2, b/2)

        If only a is even:
            gcd(a, b) = gcd(a/2, b)

        If only b is even:
            gcd(a, b) = gcd(a, b/2)

        If both are odd:
            gcd(a, b) = gcd(|a-b|, min(a,b))

    The implementation below uses bit operations for division by two.
    """
    a = abs(a)
    b = abs(b)

    if a == 0:
        return b
    if b == 0:
        return a

    common_power_of_two = 0

    while ((a | b) & 1) == 0:
        a >>= 1
        b >>= 1
        common_power_of_two += 1

    while (a & 1) == 0:
        a >>= 1

    while b != 0:
        while (b & 1) == 0:
            b >>= 1

        if a > b:
            a, b = b, a

        b -= a

    return a << common_power_of_two


def demonstrate_binary_gcd() -> None:
    print("\n" + "=" * 78)
    print("23. BINARY GCD / STEIN'S ALGORITHM")
    print("=" * 78)

    pairs = [
        (48, 18),
        (270, 192),
        (123456, 7890),
        (-1024, 768),
    ]

    for a, b in pairs:
        euclidean = gcd_euclidean(a, b)
        binary = binary_gcd(a, b)

        print(
            f"gcd({a}, {b}): "
            f"Euclidean={euclidean}, Binary={binary}, "
            f"same={euclidean == binary}"
        )


# =============================================================================
# 24. ADVANCED: GCD OF RATIONAL NUMBERS
# =============================================================================

def gcd_of_fractions(
    numerator_a: int,
    denominator_a: int,
    numerator_b: int,
    denominator_b: int,
) -> tuple[int, int]:
    """
    Compute the greatest positive rational number that divides both rational
    values under the integer-multiple interpretation.

    For:

        a/b and c/d

    a useful formula is:

        gcd(a/b, c/d)
        = gcd(a*d, c*b) / (b*d)

    followed by fraction reduction.

    Inputs must have non-zero denominators.
    """
    if denominator_a == 0 or denominator_b == 0:
        raise ValueError("Denominators cannot be zero.")

    numerator = gcd_euclidean(
        numerator_a * denominator_b,
        numerator_b * denominator_a,
    )

    denominator = abs(denominator_a * denominator_b)

    return reduce_fraction(numerator, denominator)


def demonstrate_fraction_gcd() -> None:
    print("\n" + "=" * 78)
    print("24. GCD OF RATIONAL NUMBERS")
    print("=" * 78)

    result = gcd_of_fractions(2, 3, 4, 5)

    print("gcd(2/3, 4/5) =", f"{result[0]}/{result[1]}")


# =============================================================================
# 25. GCD AND CONGRUENCES
# =============================================================================

def congruence_solvable(a: int, b: int, modulus: int) -> bool:
    """
    Determine whether:

        a*x ≡ b (mod modulus)

    has an integer solution.

    Criterion:

        gcd(a, modulus) divides b
    """
    if modulus == 0:
        raise ValueError("Modulus cannot be zero.")

    return b % gcd_euclidean(a, modulus) == 0


def demonstrate_congruence_solvability() -> None:
    print("\n" + "=" * 78)
    print("25. GCD AND LINEAR CONGRUENCES")
    print("=" * 78)

    examples = [
        (6, 8, 14),
        (6, 7, 14),
        (5, 3, 7),
    ]

    for a, b, modulus in examples:
        possible = congruence_solvable(a, b, modulus)

        print(
            f"{a}x ≡ {b} (mod {modulus}) "
            f"-> solution exists: {possible}"
        )


# =============================================================================
# 26. GCD IN CRYPTOGRAPHIC-STYLE NUMBER THEORY
# =============================================================================

def rsa_coprime_condition_demo() -> None:
    """
    RSA key generation requires choosing e such that:

        gcd(e, phi(n)) = 1

    This demonstration does not implement RSA encryption. It illustrates the
    role of GCD in selecting a valid public exponent.
    """
    print("\n" + "=" * 78)
    print("26. GCD IN NUMBER THEORY AND CRYPTOGRAPHY")
    print("=" * 78)

    phi_n = 40

    candidates = [3, 5, 7, 9, 11, 13]

    for e in candidates:
        print(
            f"e={e}, phi(n)={phi_n}, "
            f"gcd(e, phi(n))={gcd_euclidean(e, phi_n)}, "
            f"valid={are_coprime(e, phi_n)}"
        )


# =============================================================================
# 27. PERFORMANCE COMPARISON
# =============================================================================

def performance_comparison() -> None:
    """
    Compare brute force, Euclidean GCD, binary GCD, and math.gcd.

    Timing is machine-dependent, so the numbers are illustrative rather than
    universal benchmarks.
    """
    print("\n" + "=" * 78)
    print("27. PERFORMANCE COMPARISON")
    print("=" * 78)

    a = 123456789101112
    b = 9876543210

    methods = [
        ("Euclidean", gcd_euclidean),
        ("Binary", binary_gcd),
        ("math.gcd", math_gcd),
    ]

    for name, method in methods:
        start = perf_counter()

        result = method(a, b)

        elapsed = perf_counter() - start

        print(f"{name:12} -> result={result}, time={elapsed:.9f}s")

    # Brute force is deliberately omitted for large inputs because scanning
    # every candidate up to min(a, b) would be unnecessarily expensive.


# =============================================================================
# 28. ALGORITHM COMPARISON
# =============================================================================

def algorithm_comparison() -> None:
    print("\n" + "=" * 78)
    print("28. ALGORITHM COMPARISON")
    print("=" * 78)

    comparison = [
        (
            "Brute force",
            "O(min(a,b))",
            "O(1)",
            "Simple definition; educational",
        ),
        (
            "Euclidean",
            "O(log(min(a,b)))",
            "O(1)",
            "General-purpose algorithm",
        ),
        (
            "Recursive Euclidean",
            "O(log(min(a,b)))",
            "O(log(min(a,b))) stack",
            "Elegant mathematical form",
        ),
        (
            "Binary GCD",
            "Logarithmic in input magnitude",
            "O(1)",
            "Uses shifts/subtraction",
        ),
        (
            "math.gcd",
            "Implementation-dependent optimized",
            "Implementation-dependent",
            "Preferred standard-library choice",
        ),
    ]

    headers = ["Method", "Time", "Space", "Typical use"]

    print(
        f"{headers[0]:22} | "
        f"{headers[1]:30} | "
        f"{headers[2]:25} | "
        f"{headers[3]}"
    )
    print("-" * 110)

    for row in comparison:
        print(
            f"{row[0]:22} | "
            f"{row[1]:30} | "
            f"{row[2]:25} | "
            f"{row[3]}"
        )


# =============================================================================
# 29. COMMON MISTAKES
# =============================================================================

def demonstrate_common_mistakes() -> None:
    print("\n" + "=" * 78)
    print("29. COMMON MISTAKES")
    print("=" * 78)

    print(
        "Mistake 1: Testing divisibility only by one number.\n"
        "Correction: A GCD must divide every input."
    )

    print(
        "\nMistake 2: Using floating-point arithmetic for integer GCD.\n"
        "Correction: Keep exact integer arithmetic or scale fixed-precision "
        "decimal values to integers."
    )

    print(
        "\nMistake 3: Forgetting zero handling.\n"
        "Correction: gcd(0, n) is |n|; explicitly define behavior for "
        "gcd(0, 0)."
    )

    print(
        "\nMistake 4: Multiplying before dividing when calculating LCM.\n"
        "Correction: Use abs((a // gcd(a,b)) * b) to reduce intermediate size."
    )

    print(
        "\nMistake 5: Assuming prime factorization is always the fastest way.\n"
        "Correction: Euclidean GCD is normally much more efficient for "
        "ordinary integer GCD computation."
    )


# =============================================================================
# 30. VALIDATION AND CONTRACTS
# =============================================================================

def safe_gcd(a: object, b: object) -> int:
    """
    Validate inputs before computing GCD.

    bool is technically a subclass of int in Python. This implementation
    accepts it because it is integer-compatible, but applications with stricter
    domain requirements may explicitly reject bool.
    """
    if not isinstance(a, int) or not isinstance(b, int):
        raise TypeError("Both inputs must be integers.")

    return gcd_euclidean(a, b)


def demonstrate_validation() -> None:
    print("\n" + "=" * 78)
    print("30. INPUT VALIDATION")
    print("=" * 78)

    valid_inputs = [
        (12, 18),
        (-24, 36),
        (0, 25),
    ]

    for a, b in valid_inputs:
        print(f"safe_gcd({a}, {b}) = {safe_gcd(a, b)}")

    invalid_inputs = [
        (12.5, 18),
        ("12", 18),
        (12, None),
    ]

    for a, b in invalid_inputs:
        try:
            safe_gcd(a, b)
        except TypeError as error:
            print(f"safe_gcd({a!r}, {b!r}) -> {error}")


# =============================================================================
# 31. UNIT TESTS
# =============================================================================

def run_tests() -> None:
    """
    Basic correctness tests.

    Tests include:
        - positive values
        - zeros
        - negatives
        - coprime values
        - equal values
        - very large Python integers
        - agreement between implementations
    """
    print("\n" + "=" * 78)
    print("31. AUTOMATED CORRECTNESS TESTS")
    print("=" * 78)

    test_cases = [
        (0, 0, 0),
        (0, 5, 5),
        (5, 0, 5),
        (12, 18, 6),
        (18, 12, 6),
        (-12, 18, 6),
        (12, -18, 6),
        (-12, -18, 6),
        (17, 19, 1),
        (100, 100, 100),
        (270, 192, 6),
        (1071, 462, 21),
        (123456789, 987654321, math_gcd(123456789, 987654321)),
    ]

    for a, b, expected in test_cases:
        assert gcd_euclidean(a, b) == expected
        assert gcd_recursive(a, b) == expected
        assert binary_gcd(a, b) == expected
        assert math_gcd(a, b) == expected

    # Test LCM identity.
    for a, b in [(12, 18), (8, 20), (21, 28), (-12, 18)]:
        g = gcd_euclidean(a, b)
        l = lcm_using_gcd(a, b)

        if a != 0 and b != 0:
            assert g * l == abs(a * b)

    # Test fraction reduction.
    assert reduce_fraction(84, 126) == (2, 3)
    assert reduce_fraction(-45, 60) == (-3, 4)
    assert reduce_fraction(45, -60) == (-3, 4)
    assert reduce_fraction(0, 20) == (0, 1)

    # Test extended GCD.
    for a, b in [(240, 46), (48, 18), (-12, 18), (0, 15)]:
        g, x, y = extended_gcd(a, b)
        assert g == gcd_euclidean(a, b)
        assert a * x + b * y == g

    # Test modular inverses.
    assert modular_inverse(3, 11) == 4
    assert modular_inverse(10, 17) == 12

    # Test Diophantine equations.
    result = solve_linear_diophantine(15, 25, 5)
    assert result is not None
    x, y, _ = result
    assert 15 * x + 25 * y == 5

    assert solve_linear_diophantine(15, 25, 7) is None

    print(f"Passed {len(test_cases)} primary GCD test cases.")
    print("All assertions passed.")


# =============================================================================
# 32. PRACTICAL APPLICATION: TILE A RECTANGULAR BOARD
# =============================================================================

def largest_square_tile(
    width: int,
    height: int,
) -> tuple[int, int]:
    """
    Find the largest square tile side that exactly tiles a rectangle.

    The side length is:

        gcd(width, height)

    Returns:
        (tile_side, number_of_tiles)
    """
    if width <= 0 or height <= 0:
        raise ValueError("Dimensions must be positive.")

    side = gcd_euclidean(width, height)
    number_of_tiles = (width // side) * (height // side)

    return side, number_of_tiles


def demonstrate_tile_problem() -> None:
    print("\n" + "=" * 78)
    print("32. PRACTICAL APPLICATION: SQUARE TILES")
    print("=" * 78)

    width, height = 84, 126

    side, count = largest_square_tile(width, height)

    print(f"Rectangle: {width} × {height}")
    print(f"Largest exact square tile: {side} × {side}")
    print(f"Number of tiles: {count}")


# =============================================================================
# 33. PRACTICAL APPLICATION: PERIODIC EVENTS
# =============================================================================

def shared_cycle_alignment(period_a: int, period_b: int) -> int:
    """
    GCD can identify the smallest common unit for certain periodic scheduling
    or discretization problems.

    Note that the first future simultaneous occurrence is an LCM problem, not
    a GCD problem. This distinction is important.

    Here we return the greatest time unit that can evenly represent both
    periods.
    """
    return gcd_euclidean(period_a, period_b)


def demonstrate_periodic_distinction() -> None:
    print("\n" + "=" * 78)
    print("33. GCD VERSUS LCM IN PERIODIC PROBLEMS")
    print("=" * 78)

    period_a = 12
    period_b = 18

    print(f"Periods: {period_a}, {period_b}")
    print(
        "Largest common time unit:",
        shared_cycle_alignment(period_a, period_b),
    )
    print(
        "First positive simultaneous multiple:",
        lcm_using_gcd(period_a, period_b),
    )


# =============================================================================
# 34. ADVANCED PROPERTY: GCD DISTRIBUTIVITY OVER MULTIPLICATION
# =============================================================================

def demonstrate_multiplicative_properties() -> None:
    """
    Important identities include:

        gcd(ka, kb) = |k| gcd(a, b)

    and:

        gcd(a, b*c) is related to gcd(a,b) and gcd(a,c), but should not be
        simplified blindly into a product because common factors can overlap.

    A particularly useful identity is:

        gcd(a, lcm(b,c)) can be analyzed through prime exponents.

    This section demonstrates only the universally safe scaling identity.
    """
    print("\n" + "=" * 78)
    print("34. SCALING PROPERTY")
    print("=" * 78)

    a, b, k = 18, 30, 7

    left = gcd_euclidean(k * a, k * b)
    right = abs(k) * gcd_euclidean(a, b)

    print(f"gcd({k}×{a}, {k}×{b}) = {left}")
    print(f"|{k}|×gcd({a}, {b}) = {right}")
    print("Identity verified:", left == right)


# =============================================================================
# 35. GCD AS A REDUCTION OPERATION
# =============================================================================

def demonstrate_associativity() -> None:
    """
    GCD is associative:

        gcd(gcd(a,b),c) = gcd(a,gcd(b,c))

    This property is what makes reduction across an iterable possible.
    """
    print("\n" + "=" * 78)
    print("35. ASSOCIATIVITY")
    print("=" * 78)

    a, b, c = 84, 126, 210

    left = gcd_euclidean(gcd_euclidean(a, b), c)
    right = gcd_euclidean(a, gcd_euclidean(b, c))

    print(f"Left grouping:  gcd(gcd({a}, {b}), {c}) = {left}")
    print(f"Right grouping: gcd({a}, gcd({b}, {c})) = {right}")
    print("Associative:", left == right)


# =============================================================================
# 36. SECURITY AND ROBUSTNESS CONSIDERATIONS
# =============================================================================

def security_considerations() -> None:
    """
    GCD itself is deterministic and normally safe to compute, but surrounding
    application design matters.

    Important considerations:

    1. Untrusted enormous integers can consume CPU and memory.
       Python's arbitrary-precision integers are powerful but not free.

    2. Do not confuse mathematical correctness with cryptographic security.
       GCD is a mathematical primitive used in cryptography, but using GCD
       alone does not create a secure cryptographic protocol.

    3. Avoid converting attacker-controlled strings to unnecessarily enormous
       integers without application-level limits.

    4. When implementing cryptographic systems, use established cryptographic
       libraries rather than creating a protocol from basic number-theory
       primitives.
    """
    print("\n" + "=" * 78)
    print("36. SECURITY AND ROBUSTNESS CONSIDERATIONS")
    print("=" * 78)

    print("GCD itself does not require secret state.")
    print("Application risks arise primarily from unbounded or untrusted input.")
    print("Cryptographic protocols require much more than a correct GCD.")


# =============================================================================
# 37. PRODUCTION IMPLEMENTATION GUIDANCE
# =============================================================================

def production_guidance() -> None:
    """
    Production choices depend on the problem.

    For ordinary Python applications:
        math.gcd is normally the best choice.

    For education:
        gcd_euclidean clearly exposes the algorithm.

    For extended number theory:
        extended_gcd is appropriate.

    For dynamic range queries:
        GCDSegmentTree can be appropriate.

    For many static range queries:
        a sparse-table approach can offer O(1) queries after preprocessing,
        though it requires O(n log n) memory/time and is more complex.

    For very large data:
        avoid unnecessary conversion, factorization, or brute-force scans.
    """
    print("\n" + "=" * 78)
    print("37. PRODUCTION IMPLEMENTATION GUIDANCE")
    print("=" * 78)

    print("General GCD:", "math.gcd")
    print("Educational GCD:", "gcd_euclidean")
    print("Extended arithmetic:", "extended_gcd")
    print("Dynamic range GCD:", "GCDSegmentTree")


# =============================================================================
# 38. INTERACTIVE MINI DEMONSTRATION
# =============================================================================

def interactive_demo() -> None:
    """
    Optional interactive demonstration.

    Input is deliberately not required for the main program because a study
    script should remain executable in automated environments.
    """
    print("\n" + "=" * 78)
    print("38. INTERACTIVE DEMONSTRATION")
    print("=" * 78)

    print("This study script uses fixed examples so it runs without user input.")
    print("To experiment manually, call:")
    print("    gcd_euclidean(48, 18)")
    print("    gcd_many([24, 36, 60])")
    print("    extended_gcd(240, 46)")


# =============================================================================
# 39. CONCEPTUAL CHECKS
# =============================================================================

def conceptual_checks() -> None:
    """
    Check important distinctions programmatically.
    """
    print("\n" + "=" * 78)
    print("39. CONCEPTUAL CHECKS")
    print("=" * 78)

    # GCD versus LCM.
    a, b = 18, 24
    g = gcd_euclidean(a, b)
    l = lcm_using_gcd(a, b)

    print(f"For {a} and {b}:")
    print(f"  GCD = {g}")
    print(f"  LCM = {l}")

    # Coprimality.
    print(f"  Coprime = {g == 1}")

    # Common-divisor relationship.
    common = common_divisors_using_gcd(a, b)
    print(f"  Common divisors = {common}")
    print(f"  Largest common divisor = {max(common)}")


# =============================================================================
# 40. MAIN PROGRAM
# =============================================================================

def main() -> None:
    """
    Execute the complete learning sequence.
    """
    print("=" * 78)
    print("GREATEST COMMON DIVISOR: COMPLETE PYTHON STUDY GUIDE")
    print("=" * 78)
    print(
        "This program progresses from the definition of GCD to advanced "
        "number-theoretic and algorithmic applications."
    )

    explain_gcd()
    terminology_demo()
    demonstrate_brute_force()
    demonstrate_euclidean_algorithm()
    demonstrate_recursive_gcd()
    prove_euclidean_identity(48, 18)
    demonstrate_edge_cases()
    demonstrate_coprime_numbers()
    demonstrate_gcd_many()
    demonstrate_multiple_number_methods()
    demonstrate_gcd_lcm()
    demonstrate_fraction_reduction()
    demonstrate_float_warning()
    demonstrate_bezout()
    demonstrate_modular_inverse()
    demonstrate_diophantine_equation()
    demonstrate_common_divisors()
    demonstrate_coefficient_gcd()
    demonstrate_segment_tree()
    demonstrate_prefix_gcd()
    demonstrate_prime_factorization_relationship()
    verify_gcd_properties(84, 126)
    demonstrate_binary_gcd()
    demonstrate_fraction_gcd()
    demonstrate_congruence_solvability()
    rsa_coprime_condition_demo()
    performance_comparison()
    algorithm_comparison()
    demonstrate_common_mistakes()
    demonstrate_validation()
    run_tests()
    demonstrate_tile_problem()
    demonstrate_periodic_distinction()
    demonstrate_multiplicative_properties()
    demonstrate_associativity()
    security_considerations()
    production_guidance()
    interactive_demo()
    conceptual_checks()

    print("\n" + "=" * 78)
    print("END OF GCD STUDY GUIDE")
    print("=" * 78)


if __name__ == "__main__":
    main()
