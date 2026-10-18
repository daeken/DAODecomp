"""Source marker controls; redundant authored notes cannot gate native C++."""
import unittest
from rapid_native.response import parse_response,retained_response
from workers.deepseek_packet import encode

SOURCE='// FUNCTION: DAO 0x00401000\nvoid example() {}\n'
class SourceOnlyResponse(unittest.TestCase):
    def test_source_only_and_irrelevant_notes(self):
        for extra in ({},{'functions':[{'name':'completely_wrong'}]},{'functions':'irrelevant old notes'},{'anything_else':False}):
            with self.subTest(extra=extra):self.assertEqual(parse_response({'source':SOURCE,**extra},[0x401000])['source'],SOURCE)
    def test_missing_duplicate_and_extra_markers(self):
        for source in ('void example() {}',SOURCE+SOURCE,SOURCE+'// FUNCTION: DAO 0x00402000\nvoid other() {}\n',SOURCE.replace('DAO','OTHER')):
            with self.subTest(source=source):
                with self.assertRaises(ValueError):parse_response({'source':source},[0x401000])
    def test_source_and_structured_field_types(self):
        for value in ([],{}, {'source':123},{'source':''},{'source':'x'*(1024*1024+1)},{'source':SOURCE,'uncertainties':'wrong'}):
            with self.subTest(value_type=type(value).__name__):
                with self.assertRaises(ValueError):parse_response(value,[0x401000])
    def test_complete_envelope_only(self):
        content=encode({'source':SOURCE}).decode();envelope={'choices':[{'finish_reason':'stop','message':{'content':content}}]}
        self.assertEqual(retained_response(encode(envelope),[0x401000])[0]['source'],SOURCE)
        envelope['choices'][0]['finish_reason']='length'
        with self.assertRaises(ValueError):retained_response(encode(envelope),[0x401000])
        with self.assertRaises(Exception):retained_response(b'{"source":"x","source":"y"}',[0x401000])
if __name__=='__main__':unittest.main()
