def main():
    sentences_words = []
    sentences_tags = []
    read_pos_from_file("WSJ_02-21.pos", sentences_words, sentences_tags)
    existing_tags, existing_words, state_arc_to, state_emit = training(sentences_words, sentences_tags)
    wsj_24 = []
    read_words_from_file("WSJ_24.words", wsj_24)
    counter = 0
    for sentence in wsj_24:
        if counter == 1:
            break
        counter += 1
        print(sentence)
        wsj_24_pos = decode(sentence, existing_tags, existing_words, state_arc_to, state_emit)
        print(wsj_24_pos)


def read_pos_from_file(filename, sentences_words, sentences_tags):
    file = open(filename, 'r')
    words = []
    tags = []
    for line in file:
        if line == "\n":
            sentences_words.append(words.copy())
            sentences_tags.append(tags.copy())
            words.clear()
            tags.clear()
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
    viterbi[("Start", 0)] = 1
    # recursion step
    for i in range(1, T + 1):
        word = sentence[i - 1]
        if word in existing_words:
            for tag in existing_tags:
                for tag_prime in existing_tags:
                    probability = viterbi.get((tag_prime, i - 1), 0) * state_arc_to.get((tag_prime, tag), 0) * state_emit.get((tag, word), 0)
                    if viterbi.get((tag, i), 0) < probability:
                        viterbi[(tag, i)] = probability
                        back_pointer[(tag, i)] = tag_prime
        else:
            for tag in selected_tags:
                for tag_prime in existing_tags:
                    probability = viterbi.get((tag_prime, i - 1), 0) * state_arc_to.get((tag_prime, tag), 0)
                    if viterbi.get((tag, i), 0) < probability:
                        viterbi[(tag, i)] = probability
                        back_pointer[(tag, i)] = tag_prime
    # termination step
    for tag_prime in existing_tags:
        probability = viterbi.get((tag_prime, T), 0) * state_arc_to.get((tag_prime, tag), 0) * 1
        if viterbi.get(("End", T + 1), 0) < probability:
            viterbi[("End", T + 1)] = probability
            back_pointer[("End", T + 1)] = tag_prime
    back_pointer_tag = back_pointer[("End", T + 1)]
    pos.append(back_pointer_tag)
    for i in range(T, 0, -1):
        back_pointer_tag = back_pointer[(back_pointer_tag, i)]
        pos.append(back_pointer_tag)
    return pos


if __name__ == "__main__":
    main()
