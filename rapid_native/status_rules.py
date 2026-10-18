"""Generic strict reccmp-result classification; no game-specific contracts."""
def classify(score, *, original_size, expected_size, recompiled_size, mapped, unknowns, is_stub=False):
    complete=(type(original_size) is int and type(expected_size) is int and original_size==expected_size and original_size>0
              and type(recompiled_size) is int and recompiled_size>0 and mapped and not unknowns and not is_stub)
    return 'reccmp_matched' if complete and type(score) is float and score==1.0 else 'retained_unmatched'
