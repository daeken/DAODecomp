"""Explicit ownership for independently lifted original ranges. No byte concatenation."""
import hashlib


def spans(entry, rva):
    if type(rva) is not int or type(entry['body_bytes']) is not int or not 0 <= rva < 0x100000000:
        raise ValueError('invalid_owned_identity_or_count')
    ranges = entry['body_ranges']
    if not isinstance(ranges, list) or not 1 <= len(ranges) <= 64:
        raise ValueError('owned_range_budget')
    result = []
    for row in ranges:
        lo, hi = row['start_rva'], row['end_rva_inclusive']
        if type(lo) is not int or type(hi) is not int or not 0 <= lo <= hi < 0x100000000:
            raise ValueError('invalid_owned_range')
        if result and lo <= result[-1][1]:
            raise ValueError('unsorted_or_overlapping_owned_ranges')
        result.append((lo, hi))
    if result[0][0] != rva:
        raise ValueError('owned_entry_not_first_range')
    if sum(hi-lo+1 for lo, hi in result) != entry['body_bytes']:
        raise ValueError('inventory_range_length_mismatch')
    return result


def combine(parts, ownership, image_base):
    """Keep actual VAs and per-range typed trees; offsets never span a gap."""
    if len(parts) != len(ownership):
        raise ValueError('owned_lift_count')
    rows = []
    for part, (lo, hi) in zip(parts, ownership):
        if (part['mode'] != 'Bits32' or part['pc'] != image_base+lo or part['byte_length'] != hi-lo+1
                or part['decoded_bytes'] != hi-lo+1 or not part['decode_complete']
                or part['lift_errors'] or part['opaque_instructions']):
            raise ValueError('incomplete_owned_range_lift')
        expected = image_base+lo
        for row in part['instructions']:
            if row['pc'] != expected or not 1 <= row['length'] <= 15 or len(bytes.fromhex(row['raw_hex'])) != row['length']:
                raise ValueError('owned_instruction_boundary')
            expected += row['length']
        if expected != image_base+hi+1:
            raise ValueError('owned_instruction_coverage')
        rows.append(dict(start_va=image_base+lo, end_va_exclusive=image_base+hi+1,
                         slice_sha256=hashlib.sha256(bytes.fromhex(''.join(r['raw_hex'] for r in part['instructions']))).hexdigest(),
                         lift=part))
    # Instructions remain nested. Existing linear consumers must never see a fake
    # linear stream with the excluded bytes removed.
    return dict(schema='sharpretro_owned_ranges_v1', mode='Bits32', entry_va=image_base+ownership[0][0],
                owned_bytes=sum(hi-lo+1 for lo, hi in ownership), ranges=rows,
                excluded_intervals=[dict(start_va=image_base+a[1]+1,end_va_exclusive=image_base+b[0])
                                    for a,b in zip(ownership,ownership[1:]) if a[1]+1<b[0]],
                exceptional_dependencies_included=False, proof=False)
