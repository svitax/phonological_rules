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
