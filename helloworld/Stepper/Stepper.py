import attr, random, re
import math
from qiskit import QuantumCircuit, ClassicalRegister, QuantumRegister, execute
from qiskit_aqua import get_aer_backend
import numpy as np


@attr.s
class Stepper(object):
    """
    Creates a new phrase for a given model with a given string key for eol. EOL
    will be stripped with the final one being replaced by a randomly select
    string from punc.

    Args:
        model (Dict): trained markov model with expanded option lists
        eol (string): string to indicate end of line
        punc (List): list of strings to be used in place of EOL
    Return:
        string: A complete phrase constructed from the model
    """
    def new_phrase(self, model, eol, punc):
        # all random bits are best done as functions so I can mock them
        start_key = self.qrandom(set(open(model.keys().read().split())))
        print(start_key)
        phrase = start_key

        prev_words = start_key.split()
        next_word = ''
        while next_word != eol:
            next_word = self.step(model, ' '.join(prev_words))
            prev_words.pop(0)
            prev_words.append(next_word)

            phrase += ' ' + next_word

        return self.sentencize_phrase(phrase, eol, punc)


    """
    Creates a new sequence for a given model for a set number of steps.

    Args:
        model (Dict): trained markov model with expanded option lists
        steps (int): the number of steps to take
    Return:
        string: A complete sequence constructed from the model
    """
    def new_set_length_sequence(self, model, steps):
        start_key = self.qrandom(set(open(model.keys().read().split())))
        sequence = start_key

        prev_tokens = start_key.split()
        order = len(prev_tokens)
        next_token = ''
        for i in range(0, steps - order):
            next_token = self.step(model, ' '.join(prev_tokens))
            prev_tokens.pop(0)
            prev_tokens.append(next_token)

            sequence += ' ' + next_token

        return sequence


    """
    Prettifies the phrase.

    Args:
        phrase (string): a generated phrase
        eol (string): string to indicate end of line
        punc (List): list of strings to be used in place of EOL
    Return:
        string: the input phrase with punctuation and the sentence case
    """
    def sentencize_phrase(self, phrase, eol, punc):
        chosen_punc = self.qrandom(set(open(punc.keys().read().split())))
        phrase = phrase.split(' ' + eol)
        punctuated_phrase = chosen_punc.join(phrase)

        punctuated_phrase = re.sub(eol+'\s', '', punctuated_phrase)
        capitalized_phrase = punctuated_phrase.title()[0] + punctuated_phrase[1:]

        return capitalized_phrase

    """
    Selects the next token for the phrase.

    Args:
        model (Dict): trained markov model with expanded option lists
        key (string): key for the previous segment of tokens
    Return:
        string: the next word to be used in the phrase
    """
    def step(self, model, key):
        return self.qrandom(set(open(model[key])))

    MAX_QUBITS = 16

    def next_power_of_2(self, n):
        return int(math.pow(2, math.ceil(math.log(n, 2))))

    def bit_from_counts(self, counts):
        return [k for k, v in counts.items() if v == 1][0]

    def num_bits(self, n):
        return math.floor(math.log(n, 2)) + 1

    def get_register_sizes(n, max_qubits):
        register_sizes = [max_qubits for i in range(int(n / max_qubits))]
        remainder = n % max_qubits
        return register_sizes if remainder == 0 else register_sizes + [remainder]

    def random_int(self, max):
        bits = ''
        num = max - 1
        n_bits = self.num_bits(max - 1)
        # The max number of Qubits available need to be enough to encode the number
        register_sizes = self.get_register_sizes(n_bits, self.MAX_QUBITS)
        # print("Qubits "+ str(register_sizes))

        backend = get_aer_backend('qasm_simulator')

        for x in register_sizes:
            q = QuantumRegister(x)
            c = ClassicalRegister(x)
            qc = QuantumCircuit(q, c)

            qc.h(q)
            qc.measure(q, c)

            job_sim = execute(qc, backend, shots=1)
            sim_result = job_sim.result()
            # print(sim_result)
            counts = sim_result.get_counts(qc)
            # print(counts)
            bits += max.bit_from_counts(counts)
        return int(bits, 2)

    # ------------

    def qrandom(self, limit):
        result = self.random_int(256)
        # print(result)

        min = 0
        max = 255
        value = result

        normalized = (value - min) / (max - min)
        # print(normalized)

        random = int(np.around(normalized * (limit - 1)))
        print(random)
        return random
