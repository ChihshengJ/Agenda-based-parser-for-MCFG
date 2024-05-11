import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'src')))

from mcfg_parser.tree import Tree 
import pytest # type: ignore

class TestTree:
    def setup_method(self):
        self.tree = Tree("S", [Tree("NP", [Tree("D(the)"), Tree("N(dog)")]), Tree("VP", [Tree("V(barked)")])])

    def test_init(self):
        assert self.tree._data == "S"
        assert len(self.tree._children) == 2

    def test_to_tuple(self):
        assert self.tree.to_tuple() == ("S", ( ("NP", (("D(the)", ()), ("N(dog)", ()))), ("VP", (("V(barked)", ()),)) ))

    def test_hash(self):
        assert hash(self.tree) == hash(("S", ( ("NP", (("D(the)", ()), ("N(dog)", ()))), ("VP", (("V(barked)", ()),)) )))

    def test_eq(self):
        other_tree = Tree("S", [Tree("NP", [Tree("D(the)"), Tree("N(dog)")]), Tree("VP", [Tree("V(barked)")])])
        assert self.tree == other_tree

    def test_str(self):
        expected_str = "D(the) N(dog) V(barked)"
        assert str(self.tree) == expected_str

    def test_repr(self):
        assert repr(self.tree) == self.tree.to_string()

    def test_to_string(self):
        assert self.tree.to_string() == "S\n--NP\n  --D(the)\n  --N(dog)\n--VP\n  --V(barked)\n"

    def test_contains(self):
        assert "V(barked)" in self.tree
        assert "Sbar" not in self.tree

    def test_getitem(self):
        assert self.tree[0]._data == "NP"
        assert self.tree[1]._data == "VP"
        with pytest.raises(IndexError):
            _ = self.tree[2] 

    def test_index(self):
        assert self.tree.index("NP") == [(0,)]
        assert self.tree.index("VP") == [(1,)]
        assert self.tree.index("S") == [()]

    def test_relabel(self):
        label_map = lambda x: x.lower()
        relabeled_tree = self.tree.relabel(label_map)
        assert relabeled_tree.to_tuple() == ("s", ( ("np", (("d(the)", ()), ("n(dog)", ()))), ("vp", (("v(barked)", ()),)) ))




