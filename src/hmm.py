def main():
    sentences_words = []
    sentences_tags = []
    read_data_from_file("WSJ_02-21.pos", sentences_words, sentences_tags)
    for i in range(2):
        print(sentences_words[i])
        print(sentences_tags[i])
    existing_tags, state_arc_to, state_emit = training(sentences_words, sentences_tags)
    for tag in existing_tags:
        print(tag)
    print(len(existing_tags))
    counter = 0
    for item in state_arc_to:
        counter = counter + 1
        if counter == 10:
            break
        print(item)


def read_data_from_file(filename, sentences_words, sentences_tags):
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


def training(sentences_words, sentences_tags):
    existing_tags = {"Start", "End"}
    state_arc_to = {}
    state_emit = {}
    assert len(sentences_words) == len(sentences_tags)
    number_of_sentences = len(sentences_words)
    for i in range(number_of_sentences):
        words = sentences_words[i]
        tags = sentences_tags[i]
        assert len(words) == len(tags)
        number_of_words = len(words)
        state_arc_to[("Start", tags[0])] = state_arc_to.get(("Start", tags[0]), 0) + 1
        for j in range(number_of_words):
            word = words[j]
            tag = tags[j]
            existing_tags.add(tag)
            if j + 1 == number_of_words:
                state_arc_to[(tag, "End")] = state_arc_to.get((tag, "End"), 0) + 1
            else:
                next_tag = tags[j + 1]
                state_arc_to[(tag, next_tag)] = state_arc_to.get((tag, next_tag), 0) + 1
            state_emit[(tag, word)] = state_emit.get((tag, word), 0) + 1
    return existing_tags, state_arc_to, state_emit


if __name__ == "__main__":
    main()
