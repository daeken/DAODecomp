"""Freshly compare retained native compiler products with complete bounded EH graphs.

Inputs JSON contains coordinator-owned inventory/compiler/libraries paths only.
Pins are the reusable reviewed DAO intake policy, not candidate-supplied addresses.
No compiler invocation or stored experimental verdict reuse occurs.
"""
import argparse,json,sys
from pathlib import Path
if __package__ in (None,''):sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from rapid_object.eh_source_export import make_rows

def main():
 p=argparse.ArgumentParser(description=__doc__);p.add_argument('--original',type=Path,required=True);p.add_argument('--inputs',type=Path,required=True);p.add_argument('--build-folder',type=Path,required=True);p.add_argument('--output',type=Path,required=True);a=p.parse_args()
 result=make_rows(a.build_folder,a.original.read_bytes(),json.loads(a.inputs.read_text()),a.output);print(json.dumps(dict(status=result['computed_status'],verified_rows=len(result['records']),report=str(a.output/'report.json'))))
if __name__=='__main__':main()
