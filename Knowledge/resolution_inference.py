class Sentence:
    def get(self):
        raise Exception("nothing to evaluate")

    def formula(self):
        return ""

    def symbols(self):
        return set()

    @classmethod
    def validate(cls, sentence):
        if not isinstance(sentence, Sentence):
            raise TypeError("must be a logical sentence")

    @classmethod
    def parenthesize(cls, s):
        def balanced(s):
            count = 0
            for c in s:
                if c == "(":
                    count += 1
                elif c == ")":
                    if count <= 0:
                        return False
                    count -= 1
            return count == 0

        if not len(s) or s.isalpha() or (s[0] == "(" and s[-1] == ")" and balanced(s[1:-1])):
            return s
        else:
            return f"({s})"


class Symbol(Sentence):
    def __init__(self, name):
        self.name = name

    def __eq__(self, other):
        return isinstance(other, Symbol) and self.name == other.name

    def __hash__(self):
        return hash(("symbol", self.name))

    def get(self):
        return Symbol(self.name)
    def is_nested(self):
        return True

    def formula(self):
        return self.name

    def symbols(self):
        return {self.name}

    def __repr__(self):
        return f"Symbol({self.name})"


class And(Sentence):
    def __init__(self, *conjuncts):
        for c in conjuncts:
            Sentence.validate(c)
        self.conjuncts = list(conjuncts)

    def __eq__(self, other):
        return isinstance(other, And) and self.conjuncts == other.conjuncts

    def __hash__(self):
        return hash(("and", tuple(self.conjuncts)))

    def add(self, conjunct):
        Sentence.validate(conjunct)
        self.conjuncts.append(conjunct)

    def get(self):
        new_conjuncts = []
        for conjunct in self.conjuncts:
            c = conjunct.get()
            if isinstance(c, And):
                new_conjuncts.extend(c.conjuncts)
            else:
                new_conjuncts.append(c)
        return And(*new_conjuncts)
    def is_nested(self):
        for c in self.conjuncts:
            if isinstance(c, And):
                return False
            if isinstance(c, (Not, Or)) and not c.is_nested():
                return False
        return True

    def formula(self):
        if len(self.conjuncts) == 1:
            return self.conjuncts[0].formula()
        return " ∧ ".join(Sentence.parenthesize(c.formula()) for c in self.conjuncts)

    def symbols(self):
        return set.union(*[c.symbols() for c in self.conjuncts])

    def __repr__(self):
        return f"And({', '.join(repr(c) for c in self.conjuncts)})"


class Or(Sentence):
    def __init__(self, *disjuncts):
        for d in disjuncts:
            Sentence.validate(d)
        self.disjuncts = list(disjuncts)

    def __eq__(self, other):
        return isinstance(other, Or) and self.disjuncts == other.disjuncts

    def __hash__(self):
        return hash(("or", tuple(self.disjuncts)))

    def get(self):
        new_disjuncts = []
        for disjunct in self.disjuncts:
            d = disjunct.get()
            if isinstance(d, Or):
                new_disjuncts.extend(d.disjuncts)
            else:
                new_disjuncts.append(d)
        for i, d in enumerate(new_disjuncts):
            if isinstance(d, And):
                remaining = new_disjuncts[:i] + new_disjuncts[i + 1:]
                distribute = And(*[Or(c, *remaining).get() for c in d.conjuncts])
                return distribute.get()  # recursive
        return Or(*new_disjuncts)
    def is_nested(self):
        for d in self.disjuncts:
            if isinstance(d, Or):
                return False
            if isinstance(d, (And, Not)) and not d.is_nested():
                return False
        return True

    def formula(self):
        if len(self.disjuncts) == 1:
            return self.disjuncts[0].formula()
        return " ∨ ".join(Sentence.parenthesize(d.formula()) for d in self.disjuncts)

    def symbols(self):
        return set.union(*[d.symbols() for d in self.disjuncts])

    def __repr__(self):
        return f"Or({', '.join(repr(d) for d in self.disjuncts)})"


class Not(Sentence):
    def __init__(self, operand):
        Sentence.validate(operand)
        self.operand = operand

    def __eq__(self, other):
        return isinstance(other, Not) and self.operand == other.operand

    def __hash__(self):
        return hash(("not", self.operand))

    def get(self):
        if isinstance(self.operand, Not):
            return self.operand.operand.get()
        if isinstance(self.operand, And):
            return Or(*[Not(conjunct.get()) for conjunct in self.operand.conjuncts])
        if isinstance(self.operand, Or):
            return And(*[Not(disjunct.get()) for disjunct in self.operand.disjuncts])
        return Not(self.operand.get())

    def is_nested(self):
        if isinstance(self.operand, Not):
            return False
        if isinstance(self.operand, And):
            return False
        if isinstance(self.operand, Or):
            return False
        return True

    def formula(self):
        return "¬" + Sentence.parenthesize(self.operand.formula())

    def symbols(self):
        return self.operand.symbols()

    def __repr__(self):
        return f"Not({repr(self.operand)})"


class Implication(Sentence):
    def __init__(self, antecedent, consequent):
        Sentence.validate(antecedent)
        Sentence.validate(consequent)
        self.antecedent = antecedent
        self.consequent = consequent

    def __eq__(self, other):
        return isinstance(other, Implication) and self.antecedent == other.antecedent and self.consequent == other.consequent

    def __hash__(self):
        return hash(("implication", self.antecedent, self.consequent))

    def get(self):
        return Or(self.consequent.get(), Not(self.antecedent.get()))

    def formula(self):
        return f"{Sentence.parenthesize(self.antecedent.formula())} → {Sentence.parenthesize(self.consequent.formula())}"

    def symbols(self):
        return set.union(self.antecedent.symbols(), self.consequent.symbols())

    def __repr__(self):
        return f"Implication({repr(self.antecedent)}, {repr(self.consequent)})"


class Biconditional(Sentence):
    def __init__(self, left, right):
        Sentence.validate(left)
        Sentence.validate(right)
        self.left = left
        self.right = right

    def __eq__(self, other):
        return isinstance(other, Biconditional) and self.left == other.left and self.right == other.right

    def __hash__(self):
        return hash(("biconditional", self.left, self.right))

    def get(self):
        return And(
            Or(Not(self.left.get()), self.right.get()),
            Or(self.left.get(), Not(self.right.get()))
        )

    def formula(self):
        return f"{Sentence.parenthesize(self.left.formula())} ↔ {Sentence.parenthesize(self.right.formula())}"

    def symbols(self):
        return set.union(self.left.symbols(), self.right.symbols())

    def __repr__(self):
        return f"Biconditional({repr(self.left)}, {repr(self.right)})"


def nest(knowledge):
    knowledge = knowledge.get()

    if not knowledge.is_nested():
        return nest(knowledge)
    else:
        return knowledge
def complementary(clause1, clause2):
    if isinstance(clause1, (Not, Symbol)) and isinstance(clause2, (Not,Symbol)):
        if clause1 == Not(clause2).get():
            return 5
        else:
            return 1
    if isinstance(clause1, (Not,Symbol)) and isinstance(clause2, Or):
        if Not(clause1).get() in clause2.disjuncts:
            return 2
        return 0
    if isinstance(clause1, Or) and isinstance(clause2, (Not, Symbol)):
        if Not(clause2).get() in clause1.disjuncts:
            return 3
        return 0

    if isinstance(clause1, Or) and isinstance(clause2, Or):
        for d1 in clause1.disjuncts:
            if Not(d1).get() in clause2.disjuncts:
                return 4
        return 0
    return 0


def resolve(clause1, clause2, complement):
    if complement == 2:
        if Not(clause1).get() in clause2.disjuncts:
            resolvent = [d for d in clause2.disjuncts if d!=Not(clause1).get()]
            return resolvent
    if complement == 3:
        if Not(clause2).get() in clause1.disjuncts:
            resolvent = [d for d in clause1.disjuncts if d != Not(clause2).get()]
            return resolvent
    if complement == 4:
        list_c1 = clause1.disjuncts
        list_c2 = clause2.disjuncts
        resolvent = []
        for c1 in list_c1:
                if Not(c1).get() in list_c2:
                    list_c2.remove(Not(c1).get())
                resolvent.append(c1)

        union = list(set(resolvent).union(list_c2))
        return union





def check_clauses(*literals, resolved_pairs = None):
    if resolved_pairs is None:
        resolved_pairs = set()
    literals = list(literals)

    new_clauses = []
    for i, clause1 in enumerate(literals):
        for clause2 in literals[i + 1:]:
            if (clause1, clause2) in resolved_pairs:
                continue
            complement = complementary(clause1, clause2)
            if complement>1:
                resolved_pairs.add((clause1, clause2))
                if complement == 5:
                    return True
                resolvent = resolve(clause1, clause2, complement)
                if len(resolvent) == 0:
                    return True
                if len(resolvent) > 1:
                    new_clauses.append(Or(*resolvent))
                else:
                    new_clauses.append(resolvent[0])
    if not new_clauses:
        return False
    return check_clauses(*literals, *new_clauses, resolved_pairs = resolved_pairs)









def main(knowledge,query):
    knowledge = nest(knowledge)
    query = nest(query)
    knowledge.add(Not(query).get())
    literals = []
    for c in knowledge.conjuncts:
        literals.append(c)

    return check_clauses(*literals)






A = Symbol("A")
B = Symbol("B")
C = Symbol("C")
K = Symbol("K")

knowledge = And(
    Implication(A, B),
    Implication(B, C),
    A
)

query = C


result = main(knowledge, query)
print(result)



