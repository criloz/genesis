import networkx as nx
import primesieve
import ulid

BuilderGraph = nx.DiGraph()
HierarchyGraph = nx.DiGraph()

prime_iterator = primesieve.Iterator()

ClassSet = dict()

CategorySet = dict()


def show(e):
    print(e)


class Class:
    def __init__(self, builder_cats=(), source_object=None, builder_predicate=None):
        self.builder_predicate = builder_predicate
        self.id = ulid.new().str
        # link class with builder cat
        # insert in the class
        for cat in builder_cats:
            BuilderGraph.add_edge(cat.id, self.id, weight=None)
        ClassSet[self.id] = self

    @property
    def categories(self):
        for incoming in BuilderGraph.predecessors(self.id):
            yield CategorySet.get(incoming)

    def __repr__(self):
        return f'class(cats: {self.builder_cats})'

    def __call__(self, x):
        errors = []
        if self.builder_predicate(x, errors):
            return Object(x, self)
        else:
            show(errors)


class Object:
    def __init__(self, value, constructor):
        self.id = ulid.new().str
        self.value = value
        self.constructor = constructor

    def __repr__(self):
        # get categories from class generator
        names = []
        for cat in self.constructor.categories:
            if len(cat.path.split("::")) > 0:
                names.append("#" + cat.path.split("::")[1])
            else:
                names.append("#" + cat.path)
        names[-1] = names[-1].strip('#')
        return f"{' '.join(names)}({self.value})"


class Category:
    def __init__(self, path):
        self.path = path
        self.id = prime_iterator.next_prime()
        CategorySet[self.id] = self

    def add_child_boundary(self, child):
        # child has precedence over self
        HierarchyGraph.add_edge(child.id, self.id)

    def __contains__(self, other):
        return BuilderGraph.has_edge(self.id, other.constructor.id)

    def __repr__(self):
        return f'cat(id={self.id}, path={self.path})'


class Composition:
    def __init__(self, *cats):
        self.cats = cats

    def __contains__(self, other):
        result = True
        for cat in self.cats:
            result = result and other in cat
            if not result:
                break
        return result

    def __repr__(self):
        return f'cat(id={self.id}, path={self.path})'


"""
G = nx.Graph()
G.add_edge('A', 'B', weight=4)
G.add_edge('B', 'D', weight=2)
G.add_edge('A', 'C', weight=3)
G.add_edge('C', 'D', weight=4)
print(nx.shortest_path(G, 'A', 'D', weight='weight'))

a = Class([1, 2, 9, 3, 2])
z = Category('category');
print(z)
"""

# initial cats
category = Category("genesis::category")
literal = Category("genesis::literal")
number = Category("genesis::number")
str_genesis = Category("genesis::str")
char = Category("genesis::char")
functor = Category("genesis::functor")
natural = Category("genesis::natural")
rational = Category("genesis::rational")

# predicates has algebra
predicate = Category("genesis::rational")

# the order category
# the order category comes with two predicates about implementation should implement > or <
order = Category("genesis::order")


# create objects

# number literal natural, create an object
def lnn_predicate(x, error):
    if isinstance(x, int):
        if x >= 0:
            pass
        else:
            error.append({"value": str(x), "msg": "is not a natural"})
    else:
        error.append({"value": str(x), "msg": "is not a integer"})
    if len(error) > 0:
        return False
    return True


def rational_predicate(x, error):
    if isinstance(x, int):
        if x >= 0:
            pass
        else:
            error.append({"value": str(x), "msg": "is not a natural"})
    else:
        error.append({"value": str(x), "msg": "is not a integer"})
    if len(error) > 0:
        return False
    return True


natural_number_literal = Class(builder_cats=[number, literal, natural], builder_predicate=lnn_predicate)
Composition(literal, number).add_child_boundary(natural, number)

rational_number_literal = Class(builder_cats=[rational, literal, number], builder_predicate=rational_predicate)
print(natural_number_literal(70))
