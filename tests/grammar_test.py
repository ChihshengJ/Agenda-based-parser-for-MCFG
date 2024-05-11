import sys
import os
from copy import deepcopy

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'src')))

from mcfg_parser import grammar, abparser
import pytest # type: ignore

class TestMCFGRuleElement:
    def setup_method(self):
        self.element = grammar.MCFGRuleElement('NPwhdisloc', (0,2), (1,4))

    def test_init(self):
        assert self.element.variable == 'NPwhdisloc'
        assert self.element.string_variables == ((0,2), (1,4))

    def test_str(self):
        assert str(self.element) == "NPwhdisloc(02, 14)"
    
    def test_eq(self):
        other = grammar.MCFGRuleElement('NPwhdisloc', (0,2), (1,4))
        assert self.element == other

    def test_to_tuple(self):
        assert self.element.to_tuple() == ('NPwhdisloc', ((0,2), (1,4)))

    def test_hash(self):
        assert hash(self.element) == hash(('NPwhdisloc', ((0,2), (1,4))))


class TestMCFGRuleElementInstance:
    def setup_method(self):
        self.instance = grammar.MCFGRuleElementInstance('VPwhrc', (0,2), (1,4))

    def test_init(self):
        assert self.instance.variable == 'VPwhrc'
        assert self.instance.string_spans == ((0,2), (1,4))  

    def test_eq(self):
        other = grammar.MCFGRuleElementInstance('VPwhrc', (0,2), (1,4))
        assert self.instance == other

    def test_to_tuple(self):
        assert self.instance.to_tuple() == ('VPwhrc', ((0,2), (1,4)))

    def test_hash(self):
        assert hash(self.instance) == hash(('VPwhrc', ((0,2), (1,4))))

    def test_str(self):
        assert str(self.instance) == "VPwhrc([0, 2], [1, 4])"

    def test_repr(self):
        assert repr(self.instance) == "VPwhrc([0, 2], [1, 4])"


class TestMCFGRule:
    @pytest.fixture(scope='module')
    def vars(self):
        vars = {grammar.MCFGRuleElement('VPwhrc', (1,), (0,2)), 
                grammar.MCFGRuleElement('Vpres', (0,)), 
                grammar.MCFGRuleElement('Sbarwhrc', (1,), (2,)), 
                grammar.MCFGRuleElement('Swhrc', (0,), (1,)), 
                grammar.MCFGRuleElement('Nwh', (0,)), 
                grammar.MCFGRuleElement('VP', (1,))}
        return vars

    def setup_method(self):
        self.rule_1 = grammar.MCFGRule.from_string("VPwhrc(v, uw) -> Vpres(u) Sbarwhrc(v, w)")
        self.rule_2 = grammar.MCFGRule.from_string("D(the)")
    
    def test_init(self):
        assert self.rule_1.left_side == grammar.MCFGRuleElement('VPwhrc', (1,), (0,2))
        assert self.rule_1.right_side == (grammar.MCFGRuleElement('Vpres', (0,)), grammar.MCFGRuleElement('Sbarwhrc', (1,), (2,)))
        assert self.rule_2.left_side == grammar.MCFGRuleElement('D', ('the',))
        assert self.rule_2.right_side == tuple()

    def test_to_tuple(self):
        assert self.rule_1.to_tuple() == (grammar.MCFGRuleElement('VPwhrc', (1,), (0,2)), (grammar.MCFGRuleElement('Vpres', (0,)), grammar.MCFGRuleElement('Sbarwhrc', (1,), (2,))))
        assert self.rule_2.to_tuple() == (grammar.MCFGRuleElement('D', ('the',)), tuple())

    def test_hash(self):
        assert hash(self.rule_1) == hash((grammar.MCFGRuleElement('VPwhrc', (1,), (0,2)), (grammar.MCFGRuleElement('Vpres', (0,)), grammar.MCFGRuleElement('Sbarwhrc', (1,), (2,)))))
        assert hash(self.rule_2) == hash((grammar.MCFGRuleElement('D', ('the',)), tuple()))

    def test_str(self):
        assert str(self.rule_1) == "VPwhrc(1, 02) -> Vpres(0) Sbarwhrc(1, 2)"
        assert str(self.rule_2) == "D(the)"

    def test_repr(self):
        assert repr(self.rule_1) == "<Rule: VPwhrc(1, 02) -> Vpres(0) Sbarwhrc(1, 2)>"
        assert repr(self.rule_2) == "<Rule: D(the)>"
    
    def test_eq(self):
        other_1 = grammar.MCFGRule.from_string("VPwhrc(v, uw) -> Vpres(u) Sbarwhrc(v, w)")
        other_1_1 = grammar.MCFGRule.from_string("VPwhrc(u, vw) -> Vpres(u) Sbarwhrc(v, w)")
        other_2 = grammar.MCFGRule.from_string("D(the)")
        other_2_1 = grammar.MCFGRule.from_string("D(a)")
        assert self.rule_1 == other_1
        assert self.rule_1 != other_1_1
        assert self.rule_2 == other_2
        assert self.rule_2 != other_2_1
    
    def test_private_validate(self):
        with pytest.raises(ValueError):
            rule_2 = grammar.MCFGRule.from_string("VPwhrc(v, uw) -> Vpres(u) Sbarwhrc(u, w)")
            rule_3 = grammar.MCFGRule.from_string("VPwhrc(v, uw) -> Vpres(u) Sbarwhrc(a, w)")
            rule_2._validate()
            rule_3._validate()

    def test_instantiate_left_side(self):
        assert self.rule_1.instantiate_left_side(
            grammar.MCFGRuleElementInstance("Vpres", (3, 4)),
            grammar.MCFGRuleElementInstance("Sbarwhrc", (1, 2), (4, 7))) == grammar.MCFGRuleElementInstance("VPwhrc", (1, 2), (3, 7))
        assert self.rule_2.instantiate_left_side(grammar.MCFGRuleElementInstance("the", (3, 4)),) == grammar.MCFGRuleElementInstance("D", (3, 4))
        assert self.rule_1.instantiate_left_side(grammar.MCFGRuleElementInstance("Vpres", (3, 4)), grammar.MCFGRuleElementInstance("Sbarwhrc", (1, 2), (5, 7))) == None
        
    def test_build_span_map(self):
        assert self.rule_1._build_span_map(
            (grammar.MCFGRuleElementInstance("Vpres", (3, 4)),
            grammar.MCFGRuleElementInstance("Sbarwhrc", (1, 2), (4, 7)))) == {0: (3, 4), 1: (1, 2), 2: (4, 7)}

    def test_right_side_align(self):
        assert self.rule_1._right_side_aligns(
            (grammar.MCFGRuleElementInstance("Vpres", (3, 4)),
            grammar.MCFGRuleElementInstance("Sbarwhrc", (1, 2), (4, 7)))) == True       
        assert self.rule_1._right_side_aligns(
            (grammar.MCFGRuleElementInstance("NP", (3, 4)),
            grammar.MCFGRuleElementInstance("Sbarwhrc", (1, 2), (4, 7)))) == False 
    
    def test_from_string(self):
        rule_4 = grammar.MCFGRule.from_string("Swhrc(u, v) -> Nwh(u) VP(v)")
        assert rule_4 == grammar.MCFGRule(grammar.MCFGRuleElement('Swhrc', (0,), (1,)), grammar.MCFGRuleElement('Nwh', (0,)), grammar.MCFGRuleElement('VP', (1,)))

    def test_string_yield(self):
        assert self.rule_2.string_yield() == 'D'

    def test_validate(self, vars):
        assert grammar.MCFGRule(grammar.MCFGRuleElement('Swhrc', (0,), (1,)), grammar.MCFGRuleElement('Nwh', (0,)), grammar.MCFGRuleElement('VP', (1,))).validate(set(), vars) == True
        with pytest.raises(ValueError):
            assert grammar.MCFGRule(grammar.MCFGRuleElement('Swhrc', (0,), (1,)), grammar.MCFGRuleElement('Nwh', (0,)), grammar.MCFGRuleElement('NP', (1,))).validate(set(), vars) == False


class TestMCFG:
    @pytest.fixture(scope='module')
    def literal_rules(self): 
        return ["S(uv) -> NP(u) VP(v)",
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
    
    @pytest.fixture(scope='module')
    def mcfg(self, literal_rules):
        initiated_rules = {grammar.MCFGRule.from_string(r) for r in literal_rules}
        all_elements = {i for r in initiated_rules for i in deepcopy(r.right_side) + ((deepcopy(r.left_side)),)}
        start_variables = {i for i in all_elements if i.variable == 'S'}
        grammar.MultipleContextFreeGrammar.parser_class = abparser.AgendaBasedParser
        return grammar.MultipleContextFreeGrammar(
                alphabet={'the', 'a', 'greyhound', 'salmon', 'human', 'believe', 'believes', 'see', 'saw', 'who', 'which', 'does', 'did', 'that', 'with'},
                variables=all_elements,
                rules=initiated_rules,
                start_variables=start_variables)
        
    def test_init(self, mcfg: grammar.MultipleContextFreeGrammar, literal_rules):
        assert mcfg._alphabet == {'the', 'a', 'greyhound', 'salmon', 'human', 'believe', 'believes', 'see', 'saw', 'who', 'which', 'does', 'did', 'that', 'with'}
        initiated_rules = {grammar.MCFGRule.from_string(r) for r in literal_rules}
        assert mcfg._variables == {i for r in initiated_rules for i in deepcopy(r.right_side) + ((deepcopy(r.left_side)),)}
        assert mcfg._rules == initiated_rules
        assert mcfg._start_variables == {grammar.MCFGRuleElement('S', (1, 0, 2)), 
                                         grammar.MCFGRuleElement('S', (0, 2, 1)), 
                                         grammar.MCFGRuleElement('S', (1,)), 
                                         grammar.MCFGRuleElement('S', (0, 1)), 
                                         grammar.MCFGRuleElement('S', (0, 1, 2))}
        assert type(mcfg._parser) == type(abparser.AgendaBasedParser(mcfg))

    def test_call(self, mcfg: grammar.MultipleContextFreeGrammar):
        test_strings_correct = [
            ['the', 'human', 'saw', 'the', 'greyhound'], 
            ['the', 'human', 'believes', 'that', 'the', 'greyhound', 'saw', 'a', 'salmon'],
            ['which', 'human', 'that', 'saw', 'a', 'salmon', 'believes', 'the', 'greyhound'],
            ['the', 'human', 'that', 'believes', 'the', 'salmon', 'that', 'believes', 'a', 'human', 'saw', 'the', 'greyhound'],
            ['the', 'human', 'saw', 'the', 'greyhound', 'with', 'a', 'salmon']
        ]
        test_strings_incorrect = [
            ['the', 'human', 'saw', 'greyhound'], 
            ['the', 'human', 'believe', 'that', 'the', 'greyhound', 'saw', 'a', 'salmon'],
            ['who', 'saw', 'a', 'salmon'],
        ]
        test_answers=[
            {"S\n--NP\n  --D(the)\n  --N(human)\n--VP\n  --Vpres(saw)\n  --NP\n    --D(the)\n    --N(greyhound)\n"},
            {"S\n--NP\n  --D(the)\n  --N(human)\n--VP\n  --Vpres(believes)\n  --Sbar\n    --C(that)\n    --S\n      --NP\n        --D(the)\n        --N(greyhound)\n      --VP\n        --Vpres(saw)\n        --NP\n          --D(a)\n          --N(salmon)\n"},
            {"S\n--NPwh\n  --Dwh(which)\n  --Nrc\n    --C(that)\n    --Src\n      --N(human)\n      --VP\n        --Vpres(saw)\n        --NP\n          --D(a)\n          --N(salmon)\n--VP\n  --Vpres(believes)\n  --NP\n    --D(the)\n    --N(greyhound)\n"},
            {"S\n--NP\n  --D(the)\n  --Nrc\n    --C(that)\n    --Src\n      --N(human)\n      --VP\n        --Vpres(believes)\n        --NP\n          --D(the)\n          --Nrc\n            --C(that)\n            --Src\n              --N(salmon)\n              --VP\n                --Vpres(believes)\n                --NP\n                  --D(a)\n                  --N(human)\n--VP\n  --Vpres(saw)\n  --NP\n    --D(the)\n    --N(greyhound)\n",
             "S\n--NPdisloc\n  --D(the)\n  --Nrc\n    --C(that)\n    --Src\n      --N(human)\n      --VP\n        --Vpres(believes)\n        --NP\n          --D(the)\n          --Nrc\n            --C(that)\n            --Src\n              --N(salmon)\n              --VP\n                --Vpres(believes)\n                --NP\n                  --D(a)\n                  --N(human)\n--VP\n  --Vpres(saw)\n  --NP\n    --D(the)\n    --N(greyhound)\n"},
            {"S\n--NP\n  --D(the)\n  --N(human)\n--VP\n  --Vpres(saw)\n  --NP\n    --NP\n      --D(the)\n      --N(greyhound)\n    --PP\n      --P(with)\n      --NP\n        --D(a)\n        --N(salmon)\n",
             "S\n--NP\n  --D(the)\n  --N(human)\n--VP\n  --VP\n    --Vpres(saw)\n    --NP\n      --D(the)\n      --N(greyhound)\n  --PP\n    --P(with)\n    --NP\n      --D(a)\n      --N(salmon)\n"}
        ]
        for s in test_strings_correct:
            assert mcfg(s) == True
        for s in test_strings_incorrect:
            assert mcfg(s) == False
        for s, ans in zip(test_strings_correct, test_answers):
            assert {t.to_string() for t in mcfg(s, mode='parse')} == ans

    def test_validate_variable(self, mcfg:grammar.MultipleContextFreeGrammar):
        assert mcfg._validate_variables() == None
    
    def test_validate_variable(self, mcfg:grammar.MultipleContextFreeGrammar):
        assert mcfg._validate_rules() == None
    
    def test_rules(self, mcfg:grammar.MultipleContextFreeGrammar):
        assert mcfg.rules('NPwh') == {grammar.MCFGRule(grammar.MCFGRuleElement('NPwh', (0, 1, 2)), grammar.MCFGRuleElement('Dwh', (0,)), grammar.MCFGRuleElement('Nrc', (1, ), (2,))), 
                                      grammar.MCFGRule(grammar.MCFGRuleElement('NPwh', (0, 1)), grammar.MCFGRuleElement('Dwh', (0,)), grammar.MCFGRuleElement('N', (1, )))}

    def test_part_of_speech(self, mcfg:grammar.MultipleContextFreeGrammar):
        assert mcfg.parts_of_speech('saw') == {grammar.MCFGRule(grammar.MCFGRuleElement('N', ('saw',))), grammar.MCFGRule(grammar.MCFGRuleElement('Vpres', ('saw',)))}

    def test_reduce(self, mcfg:grammar.MultipleContextFreeGrammar):
        assert mcfg.reduce(grammar.MCFGRuleElementInstance('NP', (3, 8)), grammar.MCFGRuleElementInstance('VPrc', (1, 2), (2, 3))) == {grammar.MCFGRule(grammar.MCFGRuleElement('Src', (1,), (0, 2)), grammar.MCFGRuleElement('NP', (0,)), grammar.MCFGRuleElement('VPrc', (1,), (2,)))}
        
