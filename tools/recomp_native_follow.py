"""Follow observed native startup code gaps; stop for runtime or bounds review.

This is an in-process-work controller, not a schedule or a game acceptance gate.
Every iteration uses the existing byte-checked selection/build/run controller.
"""
import argparse
from pathlib import Path
import subprocess
import sys
import time
from tools import recomp
from tools.recomp_native import native_observation


MISSING = {'untranslated guest code/import target', 'untranslated guest function target'}


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', type=Path, default=recomp.ROOT / 'local/recomp/native-game')
    parser.add_argument('--steps', type=int, default=32)
    parser.add_argument('--call-depth', type=int, default=2)
    parser.add_argument('--call-limit', type=int, default=64)
    parser.add_argument('--budget', type=int, default=500000000)
    parser.add_argument('--run-timeout', type=int, default=60)
    parser.add_argument('--wine', type=Path, help='explicit Wine executable for every followed run')
    parser.add_argument('--wine-prefix', type=Path, help='explicit isolated Wine profile for every followed run')
    parser.add_argument('--wine-debug', help='explicit Wine diagnostic channels for every run')
    parser.add_argument('--restart', action='store_true', help='cold-build/run once before following the current report')
    args = parser.parse_args(argv)
    if not 1 <= args.steps <= 512 or not 0 <= args.call_depth <= 8 or not 1 <= args.call_limit <= 512:
        parser.error('invalid iteration/discovery limits')
    if args.budget <= 0 or args.run_timeout <= 0:
        parser.error('budget and timeout must be positive')
    out = args.output.absolute()
    session = out / 'follow-sessions' / str(time.time_ns())
    report = dict(status='incomplete; following observed native code gaps', game_acceptance=False, steps=[])
    with recomp.locked(out / 'follow-lock'):
        session.mkdir(parents=True, exist_ok=False)
        for index in range(args.steps):
            prior_path = out / 'run-report.json'
            previous = recomp.load(prior_path) if prior_path.exists() else None
            event = native_observation(previous) if previous else {}
            restart = index == 0 and (args.restart or previous is None)
            if not restart and (previous.get('timed_out') or event.get('reason') not in MISSING):
                report['status'] = 'incomplete; runtime/entry observation requires review'
                break
            command = [sys.executable, '-m', 'tools.recomp_native', '--output', str(out), '--run',
                       '--budget', str(args.budget), '--run-timeout', str(args.run_timeout)]
            if args.wine is not None:
                command += ['--wine', str(args.wine.absolute())]
            if args.wine_prefix is not None:
                command += ['--wine-prefix', str(args.wine_prefix.absolute())]
            if args.wine_debug is not None:
                command += ['--wine-debug=' + args.wine_debug]
            if not restart:
                command += ['--advance', '--call-depth', str(args.call_depth), '--call-limit', str(args.call_limit)]
            log = session / f'{index:04d}.log'
            with log.open('w') as stream:
                result = subprocess.run(command, cwd=recomp.ROOT, stdout=stream, stderr=subprocess.STDOUT)
            step = dict(index=index, argv=command, log=str(log), log_sha256=recomp.digest(log.read_bytes()),
                        controller_exit=result.returncode, observed_before=event)
            if result.returncode != 3:
                report['status'] = 'incomplete; selection/build requires review'
                if (out / 'build-failure.json').exists():
                    step['failure'] = recomp.load(out / 'build-failure.json')
                report['steps'].append(step)
                break
            current = recomp.load(prior_path)
            step['run_report_sha256'] = recomp.digest(prior_path.read_bytes())
            step['view'] = current['view']
            step['observed_after'] = native_observation(current)
            step['timed_out'] = current['timed_out']
            step['build_report_snapshot'] = current['build_report_snapshot']
            report['steps'].append(step)
            recomp.atomic_json(session / 'report.json', report)
            recomp.atomic_json(out / 'follow-latest.json', report)
            print(f"step {index+1}: {step['observed_after'].get('pc',0):#x} {step['observed_after'].get('reason','no code frontier')}", flush=True)
        else:
            report['status'] = 'incomplete; iteration limit reached'
        recomp.atomic_json(session / 'report.json', report)
        recomp.atomic_json(out / 'follow-latest.json', report)
        print(report['status'], flush=True)
    return 3


if __name__ == '__main__':
    raise SystemExit(main())
