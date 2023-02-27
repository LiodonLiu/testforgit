from stanza.server import CoreNLPClient
from typing import List
from typing import Tuple

input_text = '''If it was raining, I'd probably stay inside. But if it was sunny, I'd go outside and play games and stuff.'''

# Google Image Search API Info
dev_api_key = 'AIzaSyA1_KidBaLn5j27aBz8BR0gg68_IafGfqw'
project_cx = '648aff331d7b32a7a'

# doesn't work, not sure why
# project_cx = '1c1dc7279d62a82a3'
# dev_api_key = 'AIzaSyDHkSBckiZEyPHDU9B3r76vUSoUIR1ppg0'

# gis = GoogleImagesSearch(dev_api_key, project_cx)

key_phrases = []

class Edge:
    def __init__(self, dep: str = "", src_index: int = -1, src_word: str = "", target_index: int = -1, target_word: str = ""):
        self.dep: str = dep
        self.src_index: int = src_index
        self.src_word: str = src_word
        self.target_index: int = target_index
        self.target_word: str = target_word
        
    def __str__(self) -> str:
        return "[" + self.dep + ", " + str(self.src_index) + ", " + self.src_word + ", " + str(self.target_index) + ", " + self.target_word + "]"
    
    def __repr__(self) -> str:
        return str(self)

class Type_Sentence:
    def __init__(self, keywords: Tuple[str], parts_text: Tuple[str], part_ranges: Tuple[Tuple[int]], id: str):
        self.keywords: List[str] = keywords
        self.parts_text: Tuple[str] = parts_text
        self.part_ranges: Tuple[Tuple[int]] = part_ranges
        self.id: str = id

def generate_type_sentences(tokens, my_edges: List[Edge], type) -> List[Type_Sentence]: # type = "if" or "because"
    to_return = []
    ifdeps: List[Edge] = [e for e in my_edges if type in e.dep] # 寻找被提取出的my_edges中是否存在
    print(ifdeps)
    print("Done with ifdeps")
    punctuations = ['.', ',', ';', ':']
    ifdeps: List[Edge] = [i for i in ifdeps if i.src_word not in punctuations and i.target_word not in punctuations] # 防止source与target为空
    
    subjs: List[Edge] = [e for e in my_edges if "subj" in e.dep]
    xcomps: List[Edge] = [e for e in my_edges if "xcomp" in e.dep]
    advmods: List[Edge] = [e for e in my_edges if "advmod" in e.dep]
    expls: List[Edge] = [e for e in my_edges if "expl" in e.dep]
    objs: List[Edge] = [e for e in my_edges if "obj" in e.dep]
    extending: List[Edge] = subjs + xcomps + advmods + expls + objs
    
    id = 0
    for ifdep in ifdeps:
        range2 = [ifdep.src_index, ifdep.src_index]
        range1 = [ifdep.target_index, ifdep.target_index]
        cur_subjs1 = [s for s in extending if ifdep.target_index == s.target_index or ifdep.target_index == s.src_index]
        for cur_subj in cur_subjs1:
            if cur_subj.src_index > range1[1]:
                range1[1] = cur_subj.src_index
            if cur_subj.src_index < range1[0]:
                range1[0] = cur_subj.src_index
            if cur_subj.target_index > range1[1]:
                range1[1] = cur_subj.target_index
            if cur_subj.target_index < range1[0]:
                range1[0] = cur_subj.target_index
        cur_subjs2 = [s for s in extending if ifdep.src_index == s.target_index or ifdep.src_index == s.src_index]
        for cur_subj in cur_subjs2:
            if cur_subj.src_index > range2[1]:
                range2[1] = cur_subj.src_index
            if cur_subj.src_index < range2[0]:
                range2[0] = cur_subj.src_index
            if cur_subj.target_index > range2[1]:
                range2[1] = cur_subj.target_index
            if cur_subj.target_index < range2[0]:
                range2[0] = cur_subj.target_index
        str_tokens = [token.word for token in tokens]
        part1 = (" ".join(str_tokens[range1[0]:range1[1]+1])).replace(" '", "'")
        part2 = (" ".join(str_tokens[range2[0]:range2[1]+1])).replace(" '", "'")
        keywords = [ifdep.target_word, ifdep.src_word]
        to_return.append(Type_Sentence(keywords, (part1, part2), (range1, range2), id))
        id += 1
    return [r for r in to_return if r is not None]

def token_index_to_word(token_index: int, ann):
    local_sentence_index = token_index
    return_word = ""
    sentence_num = 0
    for sentence in ann.sentence:
        tokenOffsetAmt = sentence.tokenOffsetEnd - sentence.tokenOffsetBegin
        if local_sentence_index > tokenOffsetAmt:
            local_sentence_index -= tokenOffsetAmt
            sentence_num += 1
            continue
        else:
            return_word = sentence.token[local_sentence_index].word
            break
    return (return_word, token_index, sentence_num, local_sentence_index)

# range format: (start, end) including both start and end
# returns (word, overall token index, sentence index, index within sentence)
def find_important_word(token_range: Tuple[int], ann, find_even_better=True):
    # returns a list of the number of connections each token has
    token_ranking = find_num_connections_list(ann)
    # find token with highest count
    highest_val = -1
    highest_index = -1
    for i in range(token_range[0], token_range[1]+1):
        if token_ranking[i] > highest_val:
            highest_val = token_ranking[i]
            highest_index = i
    # find the corresponding word with the correct token index,
    # then feed it into another function to find if a better word exists
    if find_even_better:
        return find_more_important_word(token_index_to_word(highest_index, ann), ann)
    else:
        return token_index_to_word(highest_index, ann)

# number of enhanced++ connections for each token
def find_num_connections_list(ann):
    # find number of tokens in input
    token_num = 0
    for sentence in ann.sentence:
        token_num = sentence.tokenOffsetEnd
    print("Token num: " + str(token_num))
    token_ranking = [0]*token_num
    # add 1 for every occurence of each token to the token index of token_ranking
    for sentence in ann.sentence:
        tokenOffsetEnd = sentence.tokenOffsetBegin
        for edge in sentence.enhancedPlusPlusDependencies.edge:
            # print("Offset: " + str(tokenOffsetEnd) + ", src: " + str(edge.source) + ", " + str(edge.target))
            token_ranking[tokenOffsetEnd + edge.source - 1] += 1
            token_ranking[tokenOffsetEnd + edge.target - 1] += 1
    return token_ranking

# part of speech for each token
def find_pos_list(ann):
    # find number of tokens in input
    token_num = 0
    for sentence in ann.sentence:
        token_num = sentence.tokenOffsetEnd
    print("Token num: " + str(token_num))
    pos_list = ['']*token_num
    
    ind = 0
    for sentence in ann.sentence:
        tokenOffsetEnd = sentence.tokenOffsetBegin
        for token in sentence.token:
            pos_list[ind] = token.pos
            ind += 1
    return pos_list

def find_epp_connection_list(ann):
    # find number of tokens in input
    token_num = 0
    for sentence in ann.sentence:
        token_num = sentence.tokenOffsetEnd
    print("Token num: " + str(token_num))
    epp_connection_list = ['']*token_num

    for sentence in ann.sentence:
        tokenOffsetEnd = sentence.tokenOffsetBegin
        for edge in sentence.enhancedPlusPlusDependencies.edge:
            # print("Offset: " + str(tokenOffsetEnd) + ", src: " + str(edge.source) + ", " + str(edge.target))
            epp_connection_list[tokenOffsetEnd + edge.source - 1] += edge.dep + ";"
            epp_connection_list[tokenOffsetEnd + edge.target - 1] += edge.dep + ";"
    return epp_connection_list

def find_more_important_word(find_important_word_ouput, ann):
    return_word = find_important_word_ouput[0]
    highest_index = find_important_word_ouput[1]
    sentence_num = find_important_word_ouput[2]
    local_sentence_index = find_important_word_ouput[3]
    
    better_word_index = highest_index
    
    for sentence in ann.sentence:
        tokenOffsetEnd = sentence.tokenOffsetBegin
        for edge in sentence.enhancedPlusPlusDependencies.edge:
            priority_edges = ["advmod"]
            if edge.dep in priority_edges:
                if highest_index == tokenOffsetEnd + edge.source - 1:
                    better_word_index = tokenOffsetEnd + edge.target - 1
                if highest_index == tokenOffsetEnd + edge.target - 1:
                    better_word_index = tokenOffsetEnd + edge.source - 1
                    
    if better_word_index != highest_index:
        return token_index_to_word(better_word_index, ann)
    else:
        return find_important_word_ouput

def get_total_token_amt(ann):
    total = 0
    for sentence in ann.sentence:
        for token in sentence.token:
            total += 1
    return total

def get_token_list(ann):
    tokens = []
    for sentence in ann.sentence:
        for token in sentence.token:
            tokens.append(token.word)
    return tokens
    
if __name__ == "__main__":
    #### NLP Stuff ####
    with CoreNLPClient(
            # annotators=['tokenize','ssplit','pos','lemma','ner', 'parse', 'depparse','coref', 'openie'],
            annotators=['depparse'],
            timeout=30000,
            memory='4G') as client:
        ann = client.annotate(input_text) # all dependency annotator info https://universaldependencies.org/u/overview/enhanced-syntax.html and here https://universaldependencies.org/u/dep/index.html
        tokens = []
        my_edges = []
        for sentence in ann.sentence:
            token_offset_begin: int = int(sentence.tokenOffsetBegin)  # the starting index of each token in the sentence
            print("token_offset_begin: " + str(token_offset_begin))
            for token in sentence.token:
                tokens.append(token)
            for edge in sentence.enhancedPlusPlusDependencies.edge:
                my_edges.append(Edge(edge.dep, token_offset_begin + int(edge.source)-1, tokens[token_offset_begin+int(edge.source)-1].word, token_offset_begin + int(edge.target)-1, tokens[token_offset_begin+int(edge.target)-1].word))
        print(my_edges)
        
        results = generate_type_sentences(tokens, my_edges, "if")
        for result in results:
            if result is not []:
                print("Keywords: " + result.keywords[0] + ", " + result.keywords[1])
                print("Sentence: If " + result.parts_text[0] + " then " + result.parts_text[1] + ".")
        
        results = generate_type_sentences(tokens, my_edges, "because")
        for result in results:
            if result is not []:
                print("Keywords: " + result.keywords[0] + ", " + result.keywords[1])
                print("Sentence: " + result.parts_text[0] + " because " + result.parts_text[1] + ".")
        
        print("Done")
        
    #### Remove exact duplicates and object duplicates, then reduce to max_phrases total phrases ####