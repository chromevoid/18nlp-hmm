def main():
    sentences_words = []
    sentences_tags = []
    tags = set()
    state_arc_to = {}
    state_emit = {}
    read_data_from_file("WSJ_02-21.pos", sentences_words, sentences_tags)
    for i in range(2):
        print(sentences_words[i])
        print(sentences_tags[i])
    training(sentences_words, sentences_tags, tags, state_arc_to, state_emit)


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


def training(sentences_words, sentences_tags, tags, state_arc_to, state_emit):
    number_of_sentences = len(sentences_words)
    for i in range(number_of_sentences):
        break


if __name__ == "__main__":
    main()
