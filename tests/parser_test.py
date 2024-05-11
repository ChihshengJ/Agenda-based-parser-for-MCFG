import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'src')))

from mcfg_parser import abparser
from mcfg_parser import grammar as gr
import pytest # type: ignore
from copy import deepcopy


class TestABEntry:
    def setup_method(self):
        self.entry = abparser.ABEntry(gr.MCFGRuleElementInstance('VPrc', (1, 2), (2, 3)), 3, ((1, gr.MCFGRuleElement('N', (1,))), (2, gr.MCFGRuleElement('Vpres', (2,)))))
    
    def test_init(self):
        assert self.entry.symbol == gr.MCFGRuleElementInstance('VPrc', (1, 2), (2, 3))
        assert self.entry.index == 3
        assert self.entry.backpointers == (((1, gr.MCFGRuleElement('N', (1,))), (2, gr.MCFGRuleElement('Vpres', (2,)))),)

    def test_to_tuple(self):
        assert self.entry.to_tuple() == ('VPrc', 3, (((1, gr.MCFGRuleElement('N', (1,))), (2, gr.MCFGRuleElement('Vpres', (2,)))),))

    def test_hash(self):
        assert hash(self.entry) == hash(('VPrc', 3, (((1, gr.MCFGRuleElement('N', (1,))), (2, gr.MCFGRuleElement('Vpres', (2,)))),)))

    def test_eq(self):
        other_1 = abparser.ABEntry(gr.MCFGRuleElementInstance('VPrc', (1, 2), (2, 3)), 3, ((1, gr.MCFGRuleElement('N', (1,))), (2, gr.MCFGRuleElement('Vpres', (2,)))))
        other_2 = abparser.ABEntry(gr.MCFGRuleElementInstance('VPrc', (1, 2), (2, 3)), 3, ((1, gr.MCFGRuleElement('N', (1,))), (2, gr.MCFGRuleElement('Vroot', (2,)))))
        assert self.entry.__eq__(other_1) == True
        assert self.entry.__eq__(other_2) == False

    def test_repr(self):
        assert repr(self.entry) == "3:VPrc((1, 2), (2, 3)) -> (1, N(1), 2, Vpres(2))"

    def test_str(self):
        assert str(self.entry) == "3:VPrc((1, 2), (2, 3)) -> (1, N(1), 2, Vpres(2))"


class TestAgendaBasedParser:

    @pytest.fixture(scope='module')
    def mcfg(self):
        literal_rules = ["S(uv) -> NP(u) VP(v)",
                    "S(uv) -> NPwh(u) VP(v)",
                    "S(vuw) -> Aux(u) Swhmain(v, w)",
                    "S(uvw) -> NPdisloc(u, v) VP(w)",
                    "S(uwv) -> NPwhdisloc(u, v) VP(w)",
                    "Sbar(uv) -> C(u) S(v)",
                    "Sbarwh(v, uw) -> C(u) Swhemb(v, w)",
                    "Sbarwh(u, v) -> NPwh(u) VP(v)",
                    "Swhmain(v, uw) -> NP(u) VPwhmain(v, w)",
                    "Swhmain(w, uxv) -> NPdisloc(u, v) VPwhmain(w, x)",
                    "Swhemb(v, uw) -> NP(u) VPwhemb(v, w)",
                    "Swhemb(w, uxv) -> NPdisloc(u, v) VPwhemb(w, x)",
                    "Src(v, uw) -> NP(u) VPrc(v, w)",
                    "Src(w, uxv) -> NPdisloc(u, v) VPrc(w, x)",
                    "Src(u, v) -> N(u) VP(v)",
                    "Swhrc(u, v) -> Nwh(u) VP(v)",
                    "Swhrc(v, uw) -> NP(u) VPwhrc(v, w)",
                    "Sbarwhrc(v, uw) -> C(u) Swhrc(v, w)",
                    "VP(uv) -> Vpres(u) NP(v)",
                    "VP(uv) -> Vpres(u) Sbar(v)",
                    "VPwhmain(u, v) -> NPwh(u) Vroot(v)",
                    "VPwhmain(u, wv) -> NPwhdisloc(u, v) Vroot(w)",
                    "VPwhmain(v, uw) -> Vroot(u) Sbarwh(v, w)",
                    "VPwhemb(u, v) -> NPwh(u) Vpres(v)",
                    "VPwhemb(u, wv) -> NPwhdisloc(u, v) Vpres(w)",
                    "VPwhemb(v, uw) -> Vpres(u) Sbarwh(v, w)",
                    "VPrc(u, v) -> N(u) Vpres(v)",
                    "VPrc(v, uw) -> Vpres(u) Nrc(v, w)",
                    "VPwhrc(u, v) -> Nwh(u) Vpres(v)",
                    "VPwhrc(v, uw) -> Vpres(u) Sbarwhrc(v, w)",
                    "NP(uv) -> D(u) N(v)",
                    "NP(uvw) -> D(u) Nrc(v, w)",
                    "NPdisloc(uv, w) -> D(u) Nrc(v, w)",
                    "NPwh(uv) -> Dwh(u) N(v)",
                    "NPwh(uvw) -> Dwh(u) Nrc(v, w)",
                    "NPwhdisloc(uv, w) -> Dwh(u) Nrc(v, w)",
                    "Nrc(v, uw) -> C(u) Src(v, w)",
                    "Nrc(u, vw) -> N(u) Swhrc(v, w)",
                    "Nrc(u, vwx) -> Nrc(u, v) Swhrc(w, x)",
                    "N(uv) -> N(u) N(v)",
                    "NP(uv) -> NP(u) PP(v)",
                    "PP(uv) -> P(u) NP(v)",
                    "VP(uv) -> VP(u) PP(v)",
                    "Dwh(which)",
                    "Nwh(who)",
                    "D(the)",
                    "D(a)",
                    "N(greyhound)",
                    "N(human)",
                    "N(saw)",
                    "N(salmon)",
                    "Vpres(saw)",
                    "Vroot(see)",
                    "Vpres(believes)",
                    "Vroot(believe)",
                    "Aux(does)",
                    "Aux(did)",
                    "C(that)",
                    "P(with)"]
        initiated_rules = {gr.MCFGRule.from_string(r) for r in literal_rules}
        all_elements = {i for r in initiated_rules for i in deepcopy(r.right_side) + ((deepcopy(r.left_side)),)}
        start_variables = {i for i in all_elements if i.variable == 'S'}
        gr.MultipleContextFreeGrammar.parser_class = abparser.AgendaBasedParser
        return gr.MultipleContextFreeGrammar(
                alphabet={'the', 'a', 'greyhound', 'salmon', 'human', 'believe', 'believes', 'see', 'saw', 'who', 'which', 'does', 'did', 'that', 'with'},
                variables=all_elements,
                rules=initiated_rules,
                start_variables=start_variables) 
    
    @pytest.fixture(scope='module')
    def parser(self, mcfg):
        return abparser.AgendaBasedParser(mcfg)
    
    def test_init(self, parser: abparser.AgendaBasedParser, mcfg: gr.MultipleContextFreeGrammar):
        assert parser.grammar.alphabet == mcfg.alphabet
        assert parser.grammar.variables == mcfg.variables
        assert parser.grammar.rules == mcfg.rules
        assert parser.grammar.start_variables == mcfg.start_variables
    
    @pytest.fixture(scope='module')
    def correct_examples(self):
        return [
            ['the', 'human', 'saw', 'the', 'greyhound'], 
            ['the', 'human', 'believes', 'that', 'the', 'greyhound', 'saw', 'a', 'salmon'],
            ['which', 'human', 'that', 'saw', 'a', 'salmon', 'believes', 'the', 'greyhound'],
            ['the', 'human', 'that', 'believes', 'the', 'salmon', 'that', 'believes', 'a', 'human', 'saw', 'the', 'greyhound'],
            ['the', 'human', 'saw', 'the', 'greyhound', 'with', 'a', 'salmon']
        ]

    @pytest.fixture(scope='module')
    def incorrect_examples(self):
        return [
            ['the', 'human', 'saw', 'greyhound'], 
            ['the', 'human', 'believe', 'that', 'the', 'greyhound', 'saw', 'a', 'salmon'],
            ['who', 'saw', 'a', 'salmon'],
        ]
    
    @pytest.fixture(scope='module')
    def answers(self):
        return [
            {"S\n--NP\n  --D(the)\n  --N(human)\n--VP\n  --Vpres(saw)\n  --NP\n    --D(the)\n    --N(greyhound)\n"},
            {"S\n--NP\n  --D(the)\n  --N(human)\n--VP\n  --Vpres(believes)\n  --Sbar\n    --C(that)\n    --S\n      --NP\n        --D(the)\n        --N(greyhound)\n      --VP\n        --Vpres(saw)\n        --NP\n          --D(a)\n          --N(salmon)\n"},
            {"S\n--NPwh\n  --Dwh(which)\n  --Nrc\n    --C(that)\n    --Src\n      --N(human)\n      --VP\n        --Vpres(saw)\n        --NP\n          --D(a)\n          --N(salmon)\n--VP\n  --Vpres(believes)\n  --NP\n    --D(the)\n    --N(greyhound)\n"},
            {"S\n--NP\n  --D(the)\n  --Nrc\n    --C(that)\n    --Src\n      --N(human)\n      --VP\n        --Vpres(believes)\n        --NP\n          --D(the)\n          --Nrc\n            --C(that)\n            --Src\n              --N(salmon)\n              --VP\n                --Vpres(believes)\n                --NP\n                  --D(a)\n                  --N(human)\n--VP\n  --Vpres(saw)\n  --NP\n    --D(the)\n    --N(greyhound)\n",
             "S\n--NPdisloc\n  --D(the)\n  --Nrc\n    --C(that)\n    --Src\n      --N(human)\n      --VP\n        --Vpres(believes)\n        --NP\n          --D(the)\n          --Nrc\n            --C(that)\n            --Src\n              --N(salmon)\n              --VP\n                --Vpres(believes)\n                --NP\n                  --D(a)\n                  --N(human)\n--VP\n  --Vpres(saw)\n  --NP\n    --D(the)\n    --N(greyhound)\n"},
            {"S\n--NP\n  --D(the)\n  --N(human)\n--VP\n  --Vpres(saw)\n  --NP\n    --NP\n      --D(the)\n      --N(greyhound)\n    --PP\n      --P(with)\n      --NP\n        --D(a)\n        --N(salmon)\n",
             "S\n--NP\n  --D(the)\n  --N(human)\n--VP\n  --VP\n    --Vpres(saw)\n    --NP\n      --D(the)\n      --N(greyhound)\n  --PP\n    --P(with)\n    --NP\n      --D(a)\n      --N(salmon)\n"}
        ]
    
    def test_parse(self, parser: abparser.AgendaBasedParser, correct_examples, answers):
        for e, ans in zip(correct_examples, answers):
            assert {t.to_string() for t in parser(e, mode='parse')} == ans
    
    def test_recoginze(self, parser: abparser.AgendaBasedParser, correct_examples, incorrect_examples):
        for e in correct_examples:
            assert parser._recognize(e) == True
        
        for e in incorrect_examples:
            assert parser._recognize(e) == False

    def test_combine(self, parser: abparser.AgendaBasedParser):
        entry_1 = abparser.ABEntry(gr.MCFGRuleElementInstance('VP', (2, 5)), 3, ((2, gr.MCFGRuleElement('Vpres', (2,))), (3, gr.MCFGRuleElement('NP', (3,5)))))
        entry_2 = abparser.ABEntry(gr.MCFGRuleElementInstance('N', (1, 2)), 1, (None, None))
        answer = (gr.MCFGRuleElementInstance('Src', (1, 2), (2, 5)),)
        assert parser._combine(entry_1, entry_2) == (1, answer)

    def test_fill_chart(self, parser: abparser.AgendaBasedParser):
        answer = "['0:D((0, 1),) -> (None, None)', '1:N((1, 2),) -> (None, None)', '2:N((2, 3),) -> (None, None)', '3:Vpres((2, 3),) -> (None, None)', '4:D((3, 4),) -> (None, None)', '5:N((4, 5),) -> (None, None)', '6:NP((0, 2),) -> (0, D, 1, N)', '7:VPrc((1, 2), (2, 3)) -> (1, N, 3, Vpres)', '8:VPrc((2, 3), (2, 3)) -> (2, N, 3, Vpres)', '9:VPrc((4, 5), (2, 3)) -> (5, N, 3, Vpres)', '10:NP((3, 5),) -> (4, D, 5, N)', '11:Src((1, 2), (0, 3)) -> (6, NP, 7, VPrc)', '12:Src((2, 3), (0, 3)) -> (6, NP, 8, VPrc)', '13:Src((4, 5), (0, 3)) -> (6, NP, 9, VPrc)', '14:VP((2, 5),) -> (3, Vpres, 10, NP)', '15:Src((1, 2), (2, 5)) -> (1, N, 14, VP)', '16:Src((2, 3), (2, 5)) -> (2, N, 14, VP)', '17:Src((4, 5), (2, 5)) -> (5, N, 14, VP)', '18:S((0, 5),) -> (6, NP, 14, VP)']"
        assert str([repr(e) for e in parser._fill_chart(['the', 'human', 'saw', 'the', 'greyhound'])]) == answer

    def test_get_item(self, parser: abparser.AgendaBasedParser):
        chart = parser._fill_chart(['the', 'human', 'saw', 'the', 'greyhound'])
        assert repr(parser._get_item(chart, 6)) == "6:NP((0, 2),) -> (0, D, 1, N)"
    
    def test_construct_parses(self, parser: abparser.AgendaBasedParser):
        string = ['the', 'human', 'saw', 'the', 'greyhound']
        chart = parser._fill_chart(string)
        sv = {ele.variable for ele in parser.grammar._start_variables}
        start_nodes = [entry for entry in chart if entry.symbol.variable in sv and entry.symbol._string_spans == ((0, len(string)),)]
        answer = 'S\n--NP\n  --D(the)\n  --N(human)\n--VP\n  --Vpres(saw)\n  --NP\n    --D(the)\n    --N(greyhound)\n'
        assert repr(parser._construct_parses(chart, string, start_nodes[0])) == answer