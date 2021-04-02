import json
from typing import final

feature_matrices = open('src/phoneme.json')
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

    def __repr__(self):
        return self.symbol

    def __str__(self):
        return self.symbol

    def __hash__(self):
        return hash(self.features)

    def __eq__(self, other):
        return self.features is other.features

    def in_natural_class(self, phoneme):
        if phoneme.name == 'word boundary':
            return self.name == 'word boundary'

        # from self's features, get the equivalent features in input phoneme
        input_char_features = {
            k: phoneme.features[k] for k in self.features.keys()}

        # compare the features
        return (input_char_features == self.features)


class Not(Phoneme):
    def __init__(self, phoneme):
        self.symbol = phoneme.symbol
        self.name = 'not ' + phoneme.name
        self.features = phoneme.features

    def in_natural_class(self, phoneme):

        if phoneme.name == 'word boundary':
            return not(self.name == 'word boundary')

        input_char_features = {
            k: phoneme.features[k] for k in self.features.keys()}
        return input_char_features != self.features


class Not_But(Phoneme):
    def __init__(self, phoneme, but_env):
        self.symbol = phoneme.symbol
        self.name = 'not but ' + phoneme.name
        self.features = phoneme.features
        self.but_env = but_env

    def in_natural_class(self, phoneme):

        if phoneme.name == 'word boundary':
            return self.name == 'word boundary'
            # link.transition's keys
        input_char_features = {
            k: phoneme.features[k] for k in self.features.keys()}
        return (input_char_features != self.features) and (self.but_env.in_natural_class(phoneme))


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

    def __str__(self):
        return "(%s --%s:%s--> %s)" % (self.from_state.tag, self.transition, self.output, self.to_state.tag)

    def __add__(self, other):
        return str(self) + other

    def __radd__(self, other):
        return other + str(self)

    def equals(self, transition):
        return (self.from_state == transition.from_state) and (self.transition == transition.transition) and (self.output == transition.output) and (self.to_state == transition.to_state)


class Itself:
    features = {}


class Phonological_Rule:

    def __init__(self, start_sym, end_sym, left_env=None, right_env=None):
        self.states = []
        symbols = left_env + start_sym + right_env
        lenv = len(left_env)
        syms = len(symbols)
        renv = len(right_env)
        stsym = len(start_sym)
        # num_states = 1 + len(left_env) + len(start_sym) + len(right_env) - 1

        for i in range(len(symbols)):
            self.states.append(State(f's{i}'))

        cur_state = self.states[0]
        next_state = self.states[1]
        s = 0
        init_sym = symbols[s]
        cur_state.add_link(Transition(
            cur_state, Not(init_sym), [Itself], cur_state
        ))
        cur_state.add_link(Transition(
            cur_state, init_sym, [Itself], next_state
        ))

        # start to lenv process
        for i in range(1, lenv):
            cur_state = self.states[i]
            next_state = self.states[i+1]

            # if (symbols[0] != symbols[1]) and (symbols[1] != init_sym):
            if symbols[s+1] != init_sym:
                # Not_But(symbols[1], init_sym)
                cur_state.add_link(Transition(
                    cur_state, Not_But(symbols[s+1], init_sym), [
                        Itself], self.states[1]
                ))

            # Not(symbols[1])
            cur_state.add_link(Transition(
                cur_state, Not(symbols[s+1]), [Itself], self.states[0]
            ))
            cur_state.add_link(Transition(
                cur_state, symbols[s+1], [Itself], next_state))
            s += 1

        # lenv to end process
        for i in range(lenv, syms-1):
            cur_state = self.states[i]
            next_state = self.states[i+1]
            # if (symbols[0] != symbols[1]) and (symbols[1] != init_sym):
            if symbols[s+1] != init_sym:
                cur_state.add_link(Transition(
                    cur_state, Not_But(
                        symbols[s+1], init_sym), symbols[slice(lenv, s+1)] + [Itself], self.states[1]
                ))

            cur_state.add_link(Transition(
                cur_state, Not(
                    symbols[s+1]), symbols[slice(lenv, s+1)] + [Itself], self.states[0]
            ))

            cur_state.add_link(Transition(
                cur_state, symbols[s+1], [''], next_state))
            s += 1

        #
        cur_state = self.states[len(symbols)-1]
        cur_state.add_link(Transition(
            cur_state, symbols[s+1], end_sym+right_env, self.states[0]))

        if renv == 0:
            if symbols[s+1] != init_sym:
                cur_state.add_link(Transition(
                    cur_state, Not_But(
                        symbols[s+1], init_sym), [Itself], self.states[1]
                ))
            #
            cur_state.add_link(Transition(
                cur_state, Not(symbols[s+1]), [Itself], self.states[0]
            ))
        else:
            if symbols[s+1] != init_sym:
                cur_state.add_link(Transition(
                    cur_state, Not_But(
                        symbols[1], init_sym), symbols[slice(lenv, s+1)] + [Itself], self.states[1]
                ))
            cur_state.add_link(Transition(
                cur_state, Not(
                    symbols[s+1]), symbols[slice(lenv, s+1)] + [Itself], self.states[0]
            ))

        self.initial_state = self.states[0]
        self.terminal_states = self.states

    def get_next_state(self, current_state, character):
        for link in current_state.transitions:
            if link.transition.in_natural_class(character):
                return (link.to_state, link.output)
        return None, None

    def translate(self, string):
        phoneme_string = [Phoneme('#')]
        for character in string:
            phoneme_string.append(Phoneme(character))
        phoneme_string.append(Phoneme('#'))
        state = self.initial_state
        final_output = []
        for character in phoneme_string:
            state, output = self.get_next_state(state, character)
            for item in output:
                if item == Itself:
                    final_output.append(str(character))
                else:
                    final_output.append(str(item))

        return final_output[slice(1, -1)]
        # return ''.join(final_output[slice(1, -1)])
        # return final_output


t = Phoneme('t')
d = Phoneme('d')
a = Phoneme('a')
b = Phoneme('b')


x = Phonological_Rule([t], [d], [a, a], [b, b])
print(x.translate('aatbb'))
