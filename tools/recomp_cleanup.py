"""Conservative expression cleanup for the frozen unsigned-bitvector emitter.

General arithmetic lambda inlining could reorder reads, writes or exceptions.
The experimental literal/getter rule is opt-in and never used by cleanup_plan.
Compiler-output comparison remains a separate integration gate.
"""
from collections import Counter
from dataclasses import dataclass
import re
import shutil
import subprocess

RAW_STRING = re.compile(r'(?:u8|u|U|L)?R"([^ ()\\\t\r\n]{0,16})\(')

@dataclass(frozen=True)
class Token:
    text: str
    start: int
    end: int
    opaque: bool = False


def tokens(source):
    result = []
    i = 0
    while i < len(source):
        if source[i].isspace():
            i += 1
            continue
        start = i
        opaque = False
        if source.startswith('//', i):
            i = source.find('\n', i)
            if i < 0:
                i = len(source)
            opaque = True
        elif source.startswith('/*', i):
            end = source.find('*/', i + 2)
            if end < 0:
                raise ValueError('unterminated C++ comment')
            i = end + 2
            opaque = True
        elif source[i] == '#' and not source[source.rfind('\n', 0, i) + 1:i].strip():
            # Never rewrite a macro definition or preprocessor condition.
            while True:
                end = source.find('\n', i)
                if end < 0:
                    i = len(source)
                    break
                continued = source[i:end].rstrip('\r').endswith('\\')
                i = end + 1
                if not continued:
                    break
            opaque = True
        else:
            raw = RAW_STRING.match(source, i)
            if raw:
                end = source.find(')' + raw[1] + '"', raw.end())
                if end < 0:
                    raise ValueError('unterminated C++ raw string')
                i = end + len(raw[1]) + 2
                opaque = True
            elif source[i] in ('"', "'"):
                quote = source[i]
                i += 1
                while i < len(source):
                    if source[i] == '\\':
                        i += 2
                    elif source[i] == quote:
                        i += 1
                        break
                    else:
                        i += 1
                else:
                    raise ValueError('unterminated C++ literal')
                opaque = True
            elif source[i].isalpha() or source[i] == '_':
                i += 1
                while i < len(source) and (source[i].isalnum() or source[i] == '_'):
                    i += 1
            elif source[i].isdigit():
                i += 1
                while i < len(source) and (source[i].isalnum() or source[i] in '._'):
                    i += 1
            elif source[i:i + 2] in ('<<', '>>', '::', '->'):
                i += 2
            else:
                i += 1
        result.append(Token(source[start:i], start, i, opaque))
    return result


class Expressions:
    def __init__(self, source):
        self.source = source
        self.ts = tokens(source)
        self.pairs = {}
        stack = []
        for i, token in enumerate(self.ts):
            if token.opaque:
                continue
            if token.text in ('(', '[', '{'):
                stack.append(i)
            elif token.text in (')', ']', '}'):
                if not stack or self.ts[stack[-1]].text != {')': '(', ']': '[', '}': '{'}[token.text]:
                    raise ValueError('unbalanced lexical delimiters; cleanup requires separate review')
                opening = stack.pop()
                self.pairs[opening] = i
        if stack:
            raise ValueError('unbalanced lexical delimiters; cleanup requires separate review')

    def strip(self, a, b):
        while a < b and self.ts[a].text == '(' and self.pairs.get(a) == b - 1:
            a, b = a + 1, b - 1
        return a, b

    def raw(self, span):
        a, b = span
        return self.source[self.ts[a].start:self.ts[b - 1].end]

    def split(self, a, b, separator=','):
        result = []
        start = a
        while a < b:
            if a in self.pairs:
                a = self.pairs[a] + 1
            elif self.ts[a].text == separator:
                result.append((start, a))
                start = a = a + 1
            else:
                a += 1
        result.append((start, b))
        return result

    def call(self, a, b, name):
        a, b = self.strip(a, b)
        if (b - a < 4 or self.ts[a].text != name or self.ts[a + 1].text != '('
            or self.pairs.get(a + 1) != b - 1):
            return None
        return self.split(a + 2, b - 1)

    def uint(self, span):
        a, b = self.strip(*span)
        if b - a != 1:
            return None
        match = re.fullmatch(r'(0[xX][0-9a-fA-F]+|0|[1-9][0-9]*)(?:[uUlL]*)', self.ts[a].text)
        return int(match[1], 16 if match[1].lower().startswith('0x') else 10) if match else None

    def bit_literal(self, span):
        args = self.call(*span, 'bits')
        value = self.uint(args[0]) if args and len(args) == 1 else None
        return value if value is not None and value < 2**64 else None

    def zero_high_literal(self, span):
        a, b = self.strip(*span)
        halves = self.split(a, b, '|')
        if len(halves) != 2:
            return None
        left = self.strip(*halves[0])
        shifted = self.split(*left, '<<')
        if len(shifted) != 2 or self.bit_literal(shifted[0]) != 0 or self.uint(shifted[1]) != 64:
            return None
        return self.bit_literal(halves[1])

    def simple_register_value(self, span):
        a, b = self.strip(*span)
        masked = self.call(a, b, 'narrow')
        if masked and len(masked) == 2:
            width = self.uint(masked[1])
            if width is None or not 0 <= width <= 128:
                return False
            a, b = self.strip(*masked[0])
        args = self.call(a, b, 'read_gpr_mask')
        if not args or len(args) != 3:
            return False
        sa, sb = self.strip(*args[0])
        register, mask = self.uint(args[1]), self.uint(args[2])
        return (sb - sa == 1 and re.fullmatch(r'[A-Za-z_][A-Za-z0-9_]*', self.ts[sa].text)
                and register is not None and 0 <= register < 16 and mask is not None and mask < 2**64)

    def literal_arithmetic(self, span):
        a, b = self.strip(*span)
        if [t.text for t in self.ts[a:a + 8]] != ['[', '&', ']', '(', ')', '->', 'bits', '{']:
            return None
        close = self.pairs.get(a + 7)
        if close != b - 3 or [t.text for t in self.ts[b - 2:b]] != ['(', ')']:
            return None
        statements = self.split(a + 8, close, ';')
        if len(statements) != 4 or statements[-1][0] != statements[-1][1]:
            return None
        expressions, names = [], []
        for start, end in statements[:2]:
            if (end - start < 4 or self.ts[start].text != 'auto' or
                not re.fullmatch(r'[A-Za-z_][A-Za-z0-9_]*', self.ts[start + 1].text) or self.ts[start + 2].text != '='):
                return None
            names.append(self.ts[start + 1].text)
            expressions.append((start + 3, end))
        start, end = statements[2]
        if (names[0] == names[1] or end - start != 4 or self.ts[start].text != 'return' or
            self.ts[start + 1].text != names[0] or self.ts[start + 3].text != names[1] or
            self.ts[start + 2].text not in ('+', '-', '&', '|', '^')):
            return None
        literals = [self.bit_literal(e) is not None for e in expressions]
        getters = [self.simple_register_value(e) for e in expressions]
        if not ((literals[0] and getters[1]) or (getters[0] and literals[1])):
            return None
        # The other operand is an unsigned builtin literal: moving it across
        # the one getter has no effects. No memory access, two getter ordering,
        # user-defined temporary, division or shift is admitted by this pattern.
        return f'({self.raw(expressions[0])} {self.ts[start + 2].text} {self.raw(expressions[1])})'

    def candidates(self, inline_register_literals=False):
        result = []
        for i, token in enumerate(self.ts):
            if token.opaque:
                continue
            if token.text == '(' and i in self.pairs:
                end = self.pairs[i] + 1
                value = self.zero_high_literal((i, end))
                if value is not None and not any(t.opaque for t in self.ts[i:end]):
                    result.append((i, end, f'bits(0x{value:x}ULL)', 'zero_high_literal'))
                arithmetic = self.literal_arithmetic((i, end)) if inline_register_literals else None
                if arithmetic is not None and not any(t.opaque for t in self.ts[i:end]):
                    result.append((i, end, arithmetic, 'literal_arithmetic_lambdas'))
            if token.text != 'narrow' or i + 1 not in self.pairs or self.ts[i + 1].text != '(':
                continue
            # Object methods and qualified/possibly overloaded other helpers are
            # outside this emitter-specific rewrite.
            if i and self.ts[i - 1].text in ('.', '->', '::'):
                continue
            end = self.pairs[i + 1] + 1
            if any(t.opaque for t in self.ts[i:end]):
                continue
            args = self.call(i, end, 'narrow')
            if not args or len(args) != 2:
                continue
            width = self.uint(args[1])
            if width is None or not 0 <= width <= 128:
                continue
            nested = self.call(*args[0], 'narrow')
            inner_width = self.uint(nested[1]) if nested and len(nested) == 2 else None
            if inner_width is not None and 0 <= inner_width <= 128:
                result.append((i, end, f'narrow({self.raw(nested[0])}, {min(width, inner_width)})', 'nested_masks'))
                continue
            value = self.bit_literal(args[0])
            if value is not None:
                value &= (1 << width) - 1
                result.append((i, end, f'bits(0x{value:x}ULL)', 'constant_masks'))
                continue
            stripped = self.strip(*args[0])
            if stripped != args[0] and len(self.split(*stripped)) == 1:
                result.append((i, end, f'narrow({self.raw(stripped)}, {width})', 'argument_parentheses'))
        return result


def require_runtime(header):
    compact = re.sub(r'\s+', '', header)
    if ('usingbits=unsigned__int128;' not in compact or
        'inlinebitsnarrow(bitsvalue,unsignedwidth){returnvalue&mask(width);}' not in compact or
        'inlinebitsmask(unsignedwidth){returnwidth==128?~bits(0):(bits(1)<<width)-1;}' not in compact):
        raise ValueError('unsigned bits/narrow/mask runtime contract differs; cleanup refused')


def simplify(source, max_rounds=64, inline_register_literals=False):
    counts = Counter()
    original = source
    for _ in range(max_rounds):
        tree = Expressions(source)
        edits = []
        boundary = len(tree.ts)
        for a, b, replacement, rule in sorted(tree.candidates(inline_register_literals), key=lambda x: (x[0], -x[1]), reverse=True):
            if b > boundary or tree.raw((a, b)) == replacement:
                continue
            edits.append((tree.ts[a].start, tree.ts[b - 1].end, replacement, rule))
            boundary = a
        if not edits:
            return source, dict(rules=dict(counts), experimental_register_inlining=inline_register_literals, before_bytes=len(original.encode()),
                                after_bytes=len(source.encode()), before_narrow_calls=len(re.findall(r'\bnarrow\s*\(', original)),
                                after_narrow_calls=len(re.findall(r'\bnarrow\s*\(', source)))
        for a, b, replacement, rule in edits:
            source = source[:a] + replacement + source[b:]
            counts[rule] += 1
    raise ValueError('cleanup round budget exhausted; no candidate accepted')


def format_cpp(source):
    executable = shutil.which('clang-format')
    if not executable:
        raise ValueError('clang-format is required for formatting (or use --no-format)')
    result = subprocess.run([executable, '--assume-filename=recovered.cpp',
        '--style={BasedOnStyle: LLVM, IndentWidth: 4, ColumnLimit: 100, SortIncludes: Never, IncludeBlocks: Preserve}'],
        input=source, capture_output=True, text=True, timeout=30)
    if result.returncode:
        raise ValueError('clang-format refused candidate: ' + result.stderr)
    return result.stdout, executable
