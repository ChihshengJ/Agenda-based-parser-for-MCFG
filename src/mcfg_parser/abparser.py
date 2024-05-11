from .grammar import MultipleContextFreeGrammar, MCFGRuleElement, MCFGRuleElementInstance
from .tree import Tree
from abc import ABC
from enum import Enum

class NormalForm(Enum):
    CNF = 0
    BNF = 1
    GNF = 2

ABBackPointer = tuple[int, MCFGRuleElement]


class ABEntry():
    """
    A chart entry for an agenda based parser chart

    Parameters
    ----------
    symbol : MCFGRuleElementInstance
    index : int
    backpointers : tuple[int, MCFGRuleElement]

    Attributes
    ----------
    symbol : MCFGRuleElementInstance
    index : int
    backpointers : tuple[int, MCFGRuleElement]
    """

    def __init__(self, symbol: MCFGRuleElementInstance, index: int, *backpointers: ABBackPointer):
        self._symbol = symbol
        self._index = index
        self._backpointers = backpointers

    def to_tuple(self):
        return (self._symbol.variable, self.index, self._backpointers)
        
    def __hash__(self) -> int:
        return hash(self.to_tuple())

    def __eq__(self, other: 'ABEntry') -> bool:
        return self.to_tuple() == other.to_tuple()
    
    def __repr__(self) -> str:
        if not self.backpointers or not any(bp for bps in self.backpointers for bp in bps):
            return str(self.index) + ':' + self._symbol.variable + str(self._symbol.string_spans) + ' -> ' + ' '.join(
                f"({bp[0]}, {bp[1]})" 
                for bp in self.backpointers
            )
        else:
            return str(self.index) + ':' + self._symbol.variable + str(self._symbol.string_spans) + ' -> ' + ' '.join(
                f"({bp[0][0]}, {str(bp[0][1])}, {bp[1][0]}, {str(bp[1][1])})" 
                for bp in self.backpointers
            )

    def __str__(self) -> str:
        return self.__repr__()
    
    @property
    def symbol(self) -> MCFGRuleElementInstance:
        return self._symbol

    @property
    def backpointers(self) -> tuple[ABBackPointer, ...]:
        return self._backpointers
    
    @property
    def index(self) -> int:
        return self._index


class Parser(ABC):
    """
    An general parser class

    Parameters
    ----------
    grammar
    """
    
    def __init__(self, grammar):
        self._grammar = grammar

    def __call__(self, string, mode="recognize"):
        if mode == "recognize":
            return self._recognize(string)
        elif mode == "parse":
            return self._parse(string)            
        else:
            msg = 'mode must be "parse" or "recognize"'
            raise ValueError(msg)
        
    @property
    def grammar(self):
        return self._grammar


class AgendaBasedParser(Parser):
    """
    An agenda based parser

    Parameters
    ----------
    grammar : MultipleContextFreeGrammar
    """
    normal_form = NormalForm.CNF
    def __init__(self, grammar: MultipleContextFreeGrammar):
        self._grammar = grammar

    @property
    def grammar(self):
        return super().grammar
        
    def _parse(self, string) -> set[Tree]:
        chart = self._fill_chart(string)
        sv = {ele.variable for ele in self.grammar._start_variables}
        start_nodes = [entry for entry in chart if entry.symbol.variable in sv and entry.symbol._string_spans == ((0, len(string)),)]
        if len(start_nodes) >= 1:
            return {self._construct_parses(chart, string, s) for s in start_nodes}
        else:
            print("Unable to parse this sentence.")
        return None
        
    def _recognize(self, string):
        chart = self._fill_chart(string)
        sv = {ele.variable for ele in self.grammar._start_variables}
        return any([entry for entry in chart if entry.symbol.variable in sv and entry.symbol._string_spans == ((0, len(string)),)])
    
    def _combine(self, current: ABEntry, element: ABEntry) -> tuple[int, tuple[MCFGRuleElementInstance]]:
        reversed = 0
        possible_rules = self.grammar.reduce(current.symbol, element.symbol)
        if possible_rules == set():
            reversed = 1
            possible_rules = self.grammar.reduce(element.symbol, current.symbol)
            if possible_rules == set():
                return 0, None
            else:
                result = tuple(i for i in [r.instantiate_left_side(element.symbol, current.symbol) for r in possible_rules] if i is not None)
                return reversed, result
        else:
            result = tuple(i for i in [r.instantiate_left_side(current.symbol, element.symbol) for r in possible_rules] if i is not None)
        return reversed, result

    def _fill_chart(self, string: list[str]) -> list[ABEntry]:
        agenda = []
        for idx, word in enumerate(string):
            possible_rules = self.grammar.parts_of_speech(word)
            for n, rule in enumerate(possible_rules):
                agenda.append(ABEntry(rule.instantiate_left_side(MCFGRuleElementInstance(word, (idx, idx+1))), 0, (None, None)))
        for n, e in enumerate(agenda):
            e._index = n
        chart = []
        chart_ids = set() 
        next_id = n+1
        while agenda:
            current = agenda.pop(0)
            for element in chart:
                r, combination = self._combine(current, element)
                if combination:
                    for c in combination:
                        if r:
                            new_parse = ABEntry(c, next_id, ((element.index, element.symbol.variable), (current.index, current.symbol.variable)))
                        else:
                            new_parse = ABEntry(c, next_id, ((current.index, current.symbol.variable), (element.index, element.symbol.variable)))
                        next_id += 1 
                        agenda.append(new_parse)
            if current.index not in chart_ids:
                chart.append(current)
                chart_ids.add(current.index)
        return chart
    
    def _get_item(self, inventory: list[ABEntry], index:int) -> ABEntry:
        if inventory:
            for i in inventory:
                if i.index == index:
                    return i
        return None

    def _construct_parses(self, chart: list[ABEntry], string: str, entry: ABEntry | None = None) -> Tree:
        if not entry.backpointers or not any(bp for bps in entry.backpointers for bp in bps):
            return Tree(''.join([entry.symbol.variable, '(', string[entry.symbol.string_spans[0][0]], ')']))
        children = []
        for component_bps in entry.backpointers:
            for bp in component_bps:
                child_entry_id, _ = bp
                child_entry = self._get_item(chart, child_entry_id)
                children.append(self._construct_parses(chart, string, child_entry))
        return Tree(entry.symbol.variable, children)
        