
sentence = "It's not acceptable to spit on the floor anytime during the day"# omit period to make game more difficult

def fragment_sentence(sentence):
    sentence_list = sentence.split()
    sentence_word_count = len(sentence_list)
    max_frag_size = round(sentence_word_count/3)
    frag_list = []
    i = 0
    while i*max_frag_size <= sentence_word_count:
        frag_list.append(sentence_list[i*max_frag_size:(i + 1)*max_frag_size])
        i += 1 
    frag_list = [' '.join(words) for words in frag_list][0:3]
    
    return frag_list
