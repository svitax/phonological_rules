import json

feature_matrices = open('phoneme.json')
fm = json.load(feature_matrices)


class Phoneme:
    def __init__(self, symbol, name=None, features=None):
        if symbol == '#':
            self.symbol = '#'
            self.name = 'word boundary'
            self.features = {'boundary': True}
        else:
            self.symbol = symbol

            if name:
                self.name = name
            else:
                self.name = fm[self.symbol]['name']

            if features:
                self.features = features
            else:
                self.features = fm[self.symbol]['features']

    def in_natural_class(self, phoneme):
        if phoneme.name == 'word boundary':
            return self.name == 'word boundary'

        # from self's features, get the equivalent features in input phoneme
        input_char_features = {
            k: phoneme.feautres[k] for k in self.features.keys()}

        # compare the features
        return (input_char_features == self.features)


class State:
    def __init__(self, tag):
        self.tag = tag
        self.transitions = []

    def add_link(self, transition):
        self.transitions.append(transition)

    def equals(self, state):
        ok = (self.tag == state.tag)
        if len(self.transitions) == len(state.transitions):
            # for i in range(len(self.transitions)):
            for i, val in enumerate(self.transitions):
                ok = ok and (val == state.transitions[i])
                # ok = ok and (self.transitions[i] == state.transitions[i])
            return ok
        else:
            return False


class Transition:
    def __init__(self, from_state, transition, output, to_state):
        self.from_state = from_state
        self.transition = transition
        self.output = output
        self.to_state = to_state

    def equals(self, transition):
        return (self.from_state == transition.from_state) and (self.transition == transition.transition) and (self.output == transition.output) and (self.to_state == transition.to_state)
