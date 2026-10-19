"""Propose source-only VA-to-RVA identifier repairs; never grant match credit.

The original source and comparator stay unchanged. Every proposal must be rebuilt
and compared against the pinned original before any acceptance decision.
"""
import hashlib
import json
from pathlib import Path
import re


# VC8 permits '$' in identifiers; do not rewrite a stable-looking substring.
IDENTIFIER = re.compile(r'[A-Za-z_$][A-Za-z_0-9$]*')
STABLE_NAME = re.compile(r'(fn|g)_([0-9a-fA-F]{8})\Z')


def digest(data):
    return hashlib.sha256(data).hexdigest()


def normalize_identifiers(source, registry, image_base):
    """Return a proposed source and occurrence-counted unambiguous renames.

    Registry entries carry original VAs (integer or ``original_va`` record).
    Existing RVA spellings always win, even when another interpretation exists.
    Comments and quoted literals are copied byte-for-byte.
    """
    if type(image_base) is not int or not 0 <= image_base <= 0xffffffff:
        raise ValueError('invalid_image_base')
    changes = {}
    parts = []
    offset = 0
    while offset < len(source):
        start = offset
        if source.startswith('//', offset):
            while True:
                end = source.find('\n', offset)
                if end < 0:
                    offset = len(source)
                    break
                offset = end + 1
                if not source[start:end].rstrip('\r').endswith('\\'):
                    break
        elif source.startswith('/*', offset):
            end = source.find('*/', offset + 2)
            offset = len(source) if end < 0 else end + 2
        elif source[offset] in ('"', "'"):
            quote = source[offset]
            offset += 1
            while offset < len(source):
                if source[offset] == '\\':
                    offset += min(2, len(source) - offset)
                elif source[offset] == quote:
                    offset += 1
                    break
                else:
                    offset += 1
        else:
            token = IDENTIFIER.match(source, offset)
            if token is not None and (offset == 0 or not (source[offset - 1].isalnum() or source[offset - 1] in '_$')):
                offset = token.end()
                name = token.group()
                match = STABLE_NAME.fullmatch(name)
                canonical = f'{match[1]}_{int(match[2], 16):08x}' if match else name
                if match and canonical not in registry:
                    va = int(match[2], 16)
                    rva = va - image_base
                    replacement = f'{match[1]}_{rva:08x}' if rva >= 0 else ''
                    target = registry.get(replacement)
                    target_va = target.get('original_va') if isinstance(target, dict) else target
                    if target_va == va:
                        record = changes.setdefault(name, {'before': name, 'after': replacement, 'original_va': va, 'occurrences': 0})
                        record['occurrences'] += 1
                        parts.append(replacement)
                        continue
            else:
                offset += 1
        parts.append(source[start:offset])
    return ''.join(parts), list(changes.values())


def propose_file(source_path, report_path, output_dir, registry, image_base,
                 expected_source_sha256, expected_report_sha256):
    """Bind a new immutable local proposal to a retained compiled source/report."""
    source_path = Path(source_path)
    report_path = Path(report_path)
    source = source_path.read_bytes()
    report_bytes = report_path.read_bytes()
    if digest(source) != expected_source_sha256 or digest(report_bytes) != expected_report_sha256:
        raise ValueError('retained_artifact_hash_mismatch')
    report = json.loads(report_bytes)
    if report.get('source_sha256') != expected_source_sha256:
        raise ValueError('report_source_binding_mismatch')
    object_path = report_path.parent / 'candidate.obj'
    if digest(object_path.read_bytes()) != report.get('object_sha256'):
        raise ValueError('report_object_binding_mismatch')
    candidate, changes = normalize_identifiers(source.decode('utf-8'), registry, image_base)
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=False)
    candidate_bytes = candidate.encode('utf-8')
    (output_dir / 'candidate.cpp').write_bytes(candidate_bytes)
    provenance = {'schema_version': 1, 'status': 'unvalidated_source_proposal',
                  'original_source': str(source_path.resolve()), 'original_source_sha256': expected_source_sha256,
                  'original_report': str(report_path.resolve()), 'original_report_sha256': expected_report_sha256,
                  'original_object_sha256': report['object_sha256'],
                  'module_sha256': report.get('module_sha256'), 'image_base': image_base,
                  'candidate_source_sha256': digest(candidate_bytes), 'changes': changes,
                  'implementation_sha256': digest(Path(__file__).read_bytes())}
    (output_dir / 'provenance.json').write_text(json.dumps(provenance, indent=2) + '\n')
    return provenance
