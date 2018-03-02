def main():
    sentences_words = []
    sentences_tags = []
    read_pos_from_file("WSJ_POS_CORPUS_FOR_STUDENTS/WSJ_02-21.pos", sentences_words, sentences_tags)
    existing_tags, existing_words, state_arc_to, state_emit = training(sentences_words, sentences_tags)
    wsj_24_words = []
    wsj_24_pos = []
    read_words_from_file("WSJ_POS_CORPUS_FOR_STUDENTS/WSJ_24.words", wsj_24_words)
    for sentence in wsj_24_words:
        wsj_24_pos_one_sentence = decode(sentence, existing_tags, existing_words, state_arc_to, state_emit)
        wsj_24_pos.append(wsj_24_pos_one_sentence)
    write_pos_to_file("WSJ_24.pos", wsj_24_words, wsj_24_pos)


def read_pos_from_file(filename, sentences_words, sentences_tags):
    file = open(filename, 'r')
    words = []
    tags = []
    for line in file:
        if line == "\n":
            sentences_words.append(words)
            sentences_tags.append(tags)
            words = []
            tags = []
            continue
        line = line.strip("\n")
        words.append(line.split("\t")[0])
        tags.append(line.split("\t")[1])
    file.close()


def read_words_from_file(filename, data_words):
    file = open(filename, 'r')
    words = []
    for line in file:
        if line == "\n":
            data_words.append(words.copy())
            words.clear()
            continue
        line = line.strip("\n")
        words.append(line)
    file.close()


def write_pos_to_file(filename, data_words, data_pos):
    file = open(filename, 'w')
    assert len(data_words) == len(data_pos)
    number_of_sentences = len(data_words)
    for i in range(number_of_sentences):
        words = data_words[i]
        tags = data_pos[i]
        assert len(words) == len(tags)
        number_of_words = len(words)
        for j in range(number_of_words):
            file.write("{}\t{}\n".format(words[j], tags[j]))
        file.write("\n")
    file.close()


def training(sentences_words, sentences_tags):
    existing_tags = {"Start", "End"}
    existing_words = set()
    state_counter = {}
    state_arc_to = {}
    state_emit = {}
    assert len(sentences_words) == len(sentences_tags)
    number_of_sentences = len(sentences_words)
    for i in range(number_of_sentences):
        words = sentences_words[i]
        tags = sentences_tags[i]
        assert len(words) == len(tags)
        number_of_words = len(words)
        state_counter["Start"] = state_counter.get("Start", 0) + 1
        state_counter["End"] = state_counter.get("End", 0) + 1
        state_arc_to[("Start", tags[0])] = state_arc_to.get(("Start", tags[0]), 0) + 1
        for j in range(number_of_words):
            word = words[j]
            tag = tags[j]
            existing_tags.add(tag)
            existing_words.add(word)
            state_counter[tag] = state_counter.get(tag, 0) + 1
            if j + 1 == number_of_words:
                state_arc_to[(tag, "End")] = state_arc_to.get((tag, "End"), 0) + 1
            else:
                next_tag = tags[j + 1]
                state_arc_to[(tag, next_tag)] = state_arc_to.get((tag, next_tag), 0) + 1
            state_emit[(tag, word)] = state_emit.get((tag, word), 0) + 1
    for key in state_arc_to:
        tag = key[0]
        if tag in state_counter:
            state_arc_to[key] = state_arc_to.get(key) / state_counter.get(tag)
    for key in state_emit:
        tag = key[0]
        if tag in state_counter:
            state_emit[key] = state_emit.get(key) / state_counter.get(tag)
    return existing_tags, existing_words, state_arc_to, state_emit


def decode(sentence, existing_tags, existing_words, state_arc_to, state_emit):
    T = len(sentence)
    selected_tags = {"CD", "FW", "IN", "JJ", "JJR", "JJS", "LS",
                     "NN", "NNS", "NNP", "NNPS", "PDT",
                     "RB", "RBR", "RBS", "RP", "SYM", "UH",
                     "VB", "VBD", "VBG", "VBN", "VBP", "VBZ",
                     "Start", "End"}  # 24 + 2
    pos = []
    viterbi = {}
    back_pointer = {}
    # initialization step
    for tag in existing_tags:
        viterbi[(tag, 0)] = 0
        back_pointer[(tag, 0)] = 0
    viterbi[("Start", 0)] = 1.0
    # recursion step
    for i in range(1, T + 1):
        word = sentence[i - 1]
        if word in existing_words:
            for tag in existing_tags:
                for tag_prime in existing_tags:
                    probability = viterbi.get((tag_prime, i - 1), 0) * state_arc_to.get((tag_prime, tag),
                                                                                        0) * state_emit.get((tag, word),
                                                                                                            0)
                    if viterbi.get((tag, i), 0) <= probability:
                        viterbi[(tag, i)] = probability
                        back_pointer[(tag, i)] = tag_prime
        else:
            if i > 1 and word[0].isupper() and word.endswith("s"):
                for tag in existing_tags:
                    for tag_prime in existing_tags:
                        if tag == "NNPS":
                            print(word)
                            probability = viterbi.get((tag_prime, i - 1), 0) * state_arc_to.get((tag_prime, tag), 0) * 0.9
                            if viterbi.get((tag, i), 0) <= probability:
                                viterbi[(tag, i)] = probability
                                back_pointer[(tag, i)] = tag_prime
                        else:
                            probability = viterbi.get((tag_prime, i - 1), 0) * state_arc_to.get((tag_prime, tag), 0) * 0.1
                            if viterbi.get((tag, i), 0) <= probability:
                                viterbi[(tag, i)] = probability
                                back_pointer[(tag, i)] = tag_prime
            elif i > 1 and word[0].isupper() and not word.endswith("s"):
                for tag in existing_tags:
                    for tag_prime in existing_tags:
                        if tag == "NNP":
                            probability = viterbi.get((tag_prime, i - 1), 0) * state_arc_to.get((tag_prime, tag), 0) * 0.9
                            if viterbi.get((tag, i), 0) <= probability:
                                viterbi[(tag, i)] = probability
                                back_pointer[(tag, i)] = tag_prime
                        else:
                            probability = viterbi.get((tag_prime, i - 1), 0) * state_arc_to.get((tag_prime, tag), 0) * 0.1
                            if viterbi.get((tag, i), 0) <= probability:
                                viterbi[(tag, i)] = probability
                                back_pointer[(tag, i)] = tag_prime
            elif word.endswith("ly"):
                for tag in existing_tags:
                    for tag_prime in existing_tags:
                        if tag == "RB":
                            probability = viterbi.get((tag_prime, i - 1), 0) * state_arc_to.get((tag_prime, tag), 0) * 0.9
                            if viterbi.get((tag, i), 0) <= probability:
                                viterbi[(tag, i)] = probability
                                back_pointer[(tag, i)] = tag_prime
                        else:
                            probability = viterbi.get((tag_prime, i - 1), 0) * state_arc_to.get((tag_prime, tag), 0) * 0.1
                            if viterbi.get((tag, i), 0) <= probability:
                                viterbi[(tag, i)] = probability
                                back_pointer[(tag, i)] = tag_prime
            elif word.endswith("ing"):
                for tag in existing_tags:
                    for tag_prime in existing_tags:
                        if tag == "VBG":
                            probability = viterbi.get((tag_prime, i - 1), 0) * state_arc_to.get((tag_prime, tag), 0) * 0.5
                            if viterbi.get((tag, i), 0) <= probability:
                                viterbi[(tag, i)] = probability
                                back_pointer[(tag, i)] = tag_prime
                        elif tag == "JJ":
                            probability = viterbi.get((tag_prime, i - 1), 0) * state_arc_to.get((tag_prime, tag),
                                                                                                0) * 0.4
                            if viterbi.get((tag, i), 0) <= probability:
                                viterbi[(tag, i)] = probability
                                back_pointer[(tag, i)] = tag_prime
                        else:
                            probability = viterbi.get((tag_prime, i - 1), 0) * state_arc_to.get((tag_prime, tag), 0) * 0.1
                            if viterbi.get((tag, i), 0) <= probability:
                                viterbi[(tag, i)] = probability
                                back_pointer[(tag, i)] = tag_prime
            elif word.endswith("ed"):
                for tag in existing_tags:
                    for tag_prime in existing_tags:
                        if tag == "VBD":
                            probability = viterbi.get((tag_prime, i - 1), 0) * state_arc_to.get((tag_prime, tag), 0) * 0.5
                            if viterbi.get((tag, i), 0) <= probability:
                                viterbi[(tag, i)] = probability
                                back_pointer[(tag, i)] = tag_prime
                        elif tag == "JJ":
                            probability = viterbi.get((tag_prime, i - 1), 0) * state_arc_to.get((tag_prime, tag),
                                                                                                0) * 0.4
                            if viterbi.get((tag, i), 0) <= probability:
                                viterbi[(tag, i)] = probability
                                back_pointer[(tag, i)] = tag_prime
                        else:
                            probability = viterbi.get((tag_prime, i - 1), 0) * state_arc_to.get((tag_prime, tag), 0) * 0.1
                            if viterbi.get((tag, i), 0) <= probability:
                                viterbi[(tag, i)] = probability
                                back_pointer[(tag, i)] = tag_prime
            else:
                for tag in existing_tags:
                    for tag_prime in existing_tags:
                        if tag in selected_tags:
                            probability = viterbi.get((tag_prime, i - 1), 0) * state_arc_to.get((tag_prime, tag), 0) * 0.9
                            if viterbi.get((tag, i), 0) <= probability:
                                viterbi[(tag, i)] = probability
                                back_pointer[(tag, i)] = tag_prime
                        else:
                            probability = viterbi.get((tag_prime, i - 1), 0) * state_arc_to.get((tag_prime, tag), 0) * 0.1
                            if viterbi.get((tag, i), 0) <= probability:
                                viterbi[(tag, i)] = probability
                                back_pointer[(tag, i)] = tag_prime
    # termination step
    for tag_prime in existing_tags:
        probability = viterbi.get((tag_prime, T), 0) * state_arc_to.get((tag_prime, "End"), 0) * 1
        if viterbi.get(("End", T + 1), 0) <= probability:
            viterbi[("End", T + 1)] = probability
            back_pointer[("End", T + 1)] = tag_prime
    back_pointer_tag = back_pointer[("End", T + 1)]
    pos.append(back_pointer_tag)
    for i in range(T, 1, -1):
        back_pointer_tag = back_pointer[(back_pointer_tag, i)]
        pos.append(back_pointer_tag)
    return pos[::-1]


if __name__ == "__main__":
    main()
