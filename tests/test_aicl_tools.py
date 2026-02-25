from __future__ import annotations

import unittest

from tools.parse_aicl import parse_fields
from tools.validate_aicl import validate_text


class ParseAICLTests(unittest.TestCase):
    def test_parse_basic_message(self) -> None:
        text = """
MSG{
I:ASK
O:dataset/customer_churn_q1
C:deadline=2026-02-26T18:00+08;cost<=0.2
S:{conf=0.81,ver=1.0,trace=ex_ask_001}
}
"""
        got = parse_fields(text)
        self.assertEqual(got["I"], "ASK")
        self.assertEqual(got["O"], "dataset/customer_churn_q1")
        self.assertEqual(got["S"]["trace"], "ex_ask_001")
        self.assertAlmostEqual(got["S"]["conf"], 0.81)

    def test_parse_nested_object_and_list(self) -> None:
        text = """
MSG{
I:NEGOTIATE
O:release/2026Q1
H:{required=true,options=[allow,delay,reject],meta={owner=agent_risk}}
S:{conf=0.61,ver=1.0,trace=ex_neg_001}
}
"""
        got = parse_fields(text)
        self.assertTrue(got["H"]["required"])
        self.assertEqual(got["H"]["options"], ["allow", "delay", "reject"])
        self.assertEqual(got["H"]["meta"]["owner"], "agent_risk")


class ValidateAICLTests(unittest.TestCase):
    def test_validate_ok(self) -> None:
        text = """
MSG{
I:ASK
O:task/t1
S:{conf=0.80,ver=1.0,trace=t1}
}
"""
        errs = validate_text(text)
        self.assertEqual(errs, [])

    def test_invalid_intent(self) -> None:
        text = """
MSG{
I:WHATEVER
O:task/t1
S:{conf=0.80,ver=1.0,trace=t1}
}
"""
        errs = validate_text(text)
        codes = [e.code for e in errs]
        self.assertIn("E002_INVALID_INTENT", codes)

    def test_invalid_confidence_range(self) -> None:
        text = """
MSG{
I:ASK
O:task/t1
S:{conf=1.80,ver=1.0,trace=t1}
}
"""
        errs = validate_text(text)
        codes = [e.code for e in errs]
        self.assertIn("E003_INVALID_CONFIDENCE_RANGE", codes)


if __name__ == "__main__":
    unittest.main()

