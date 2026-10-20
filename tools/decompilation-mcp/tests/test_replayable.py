"""Exercise shared portable recovery/frontier/encoding checks in the standalone runner."""
import importlib.util
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]


def load_shared(name):
    spec = importlib.util.spec_from_file_location(name, ROOT / 'tests' / (name + '.py'))
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


RecoveredIrTests = load_shared('test_replayable_ir').RecoveredIrTests
PipelineBoundaryTests = load_shared('test_replayable_pipeline').PipelineBoundaryTests

TransportGuardTests = load_shared('test_replayable_transport').TransportGuardTests
TransportBoundaryTests = load_shared('test_replayable_transport').TransportBoundaryTests

# The open stack fixtures import the shared IR builders by their test module name.
import sys
sys.path.insert(0,str(ROOT / 'tests'))
StackArgumentTests = load_shared('test_replayable_stackargs').StackArgumentTests
StackIntegrationTests = load_shared('test_replayable_stackargs').StackIntegrationTests
StackDependencyTests = load_shared('test_replayable_stackargs').StackDependencyTests

ConditionalTests = load_shared('test_replayable_conditional').ConditionalTests
ConditionalDependencyTests = load_shared('test_replayable_conditional').ConditionalDependencyTests
ConditionalIntegrationTests = load_shared('test_replayable_conditional').ConditionalIntegrationTests

FlowEhTests = load_shared('test_replayable_flow_eh').FlowEhTests
EhScanTests = load_shared('test_replayable_flow_eh').EhScanTests
EhDependencyTests = load_shared('test_replayable_flow_eh').EhDependencyTests

TailAdapterTests = load_shared('test_replayable_tail_adapters').TailAdapterTests
TailAdapterDependencyTests = load_shared('test_replayable_tail_adapters').TailAdapterDependencyTests
TailAdapterIntegrationTests = load_shared('test_replayable_tail_adapters').TailAdapterIntegrationTests

BatchPipelineTests = load_shared('test_replayable_batch_pipeline').BatchPipelineTests
BatchDispatchTests = load_shared('test_replayable_batch_pipeline').BatchDispatchTests
GuestBatchTests = load_shared('test_replayable_guest_batch').GuestBatchTests

ByValueTests = load_shared('test_replayable_byvalue').ByValueTests
UndefinedWireTests = load_shared('test_replayable_byvalue').UndefinedWireTests

BatchDecisionDocumentTests = load_shared('test_replayable_byvalue').BatchDecisionDocumentTests

LoopTests = load_shared('test_replayable_loops').LoopTests
OrderedMemoryTests = load_shared('test_replayable_ordered_memory').OrderedMemoryTests

# The bounded encoding lane keeps its exact comparator and typed crosscheck tests.
sys.path.insert(0,str(ROOT))
EncodingEquivalenceTests = load_shared('test_encoding_equivalence').EncodingEquivalenceTests
EncodingPipelineTests = load_shared('test_replayable_encoding').EncodingPipelineTests
EncodingBridgeTests = load_shared('test_replayable_encoding').EncodingBridgeTests

TerminalCallTests = load_shared('test_replayable_terminal_calls').TerminalCallTests
RuntimeBindingTests = load_shared('test_replayable_terminal_calls').RuntimeBindingTests
MutableFlowTests = load_shared('test_replayable_terminal_calls').MutableFlowTests
ReceiverLayoutTests = load_shared('test_replayable_terminal_calls').ReceiverLayoutTests

EffectRelationTests = load_shared('test_replayable_effect_relation').EffectRelationTests
EffectCfgTests = load_shared('test_replayable_effect_relation').EffectCfgTests
EffectCertificateBoundaryTests = load_shared('test_replayable_effect_relation').EffectCertificateBoundaryTests
AbiEffectsPipelineTests = load_shared('test_replayable_abi_effects').AbiEffectsPipelineTests

TypedReceiverTests = load_shared('test_replayable_receiver_fields').TypedReceiverTests

ScalarSourceTests = load_shared('test_replayable_scalar_source').ScalarSourceTests
