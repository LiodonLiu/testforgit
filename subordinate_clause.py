from typing import List
from typing import Tuple

input_text = '''If it was raining, I'd probably stay inside. But if it was sunny, I'd go outside and play games and stuff.'''

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

def sentences_with_ref(tokens, my_edges: List[Edge]) -> List[Type_Sentence]:
    to_return = []
    ifdeps: List[Edge] = [e for e in my_edges if "nsubj" in e.dep] # 寻找被提取出的my_edges中是否存在nsubj关系
    print(ifdeps)
    print("Done with ifdeps")
    punctuations = ['.', ',', ';', ':']
    ifdeps: List[Edge] = [i for i in ifdeps if i.src_word not in punctuations and i.target_word not in punctuations] # 防止source与target为标点
    
    subjs: List[Edge] = [e for e in my_edges if "subj" in e.dep and e.dep != "nsubj"]            # 它其实是把csubj等含subj的关系全都包含进来了（除了nsubj）
    xcomps: List[Edge] = [e for e in my_edges if "xcomp" in e.dep]
    advmods: List[Edge] = [e for e in my_edges if "advmod" in e.dep]
    expls: List[Edge] = [e for e in my_edges if "expl" in e.dep]
    objs: List[Edge] = [e for e in my_edges if "obj" in e.dep]
    obls: List[Edge] = [e for e in my_edges if "obl" in e.dep]
    compounds:List[Edge] = [e for e in my_edges if "compound" in e.dep]
    dets:List[Edge] = [e for e in my_edges if "det" in e.dep]
    nmods:List[Edge] = [e for e in my_edges if "nmod" in e.dep]

    extending: List[Edge] = subjs + xcomps + advmods + expls + objs + obls + compounds + dets
    
    id = 0
    for i in range(len(ifdeps)):
        ifdep = ifdeps[i]

        range1 = [ifdep.target_index, ifdep.src_index]
        range2 = [ifdep.src_index, ifdep.src_index]

        cur_subjs1 = [s for s in extending if ifdep.src_index == s.target_index or ifdep.src_index == s.src_index]
        for cur_subj in cur_subjs1:
            if cur_subj.src_index > range1[1]:
                range1[1] = cur_subj.src_index
            if cur_subj.src_index < range1[0]:
                range1[0] = cur_subj.src_index
            if cur_subj.target_index > range1[1]:
                range1[1] = cur_subj.target_index
            if cur_subj.target_index < range1[0]:
                range1[0] = cur_subj.target_index

        for e in my_edges:
            if "conj" in e.dep:
                if ifdep.src_index == e.target_index:
                    range2 = [e.src_index,e.target_index]

        cur_subjs2 = [s for s in dets if ifdep.target_index == s.target_index or ifdep.target_index == s.src_index]
        for cur_subj in cur_subjs2:
            if cur_subj.src_index > range1[1]:
                range1[1] = cur_subj.src_index
            if cur_subj.src_index < range1[0]:
                range1[0] = cur_subj.src_index
            if cur_subj.target_index > range1[1]:
                range1[1] = cur_subj.target_index
            if cur_subj.target_index < range1[0]:
                range1[0] = cur_subj.target_index

        objhandles: List[Edge] = [e for e in objs if ifdep.src_index == e.target_index or ifdep.src_index == e.src_index]# 提取出所有和src_word有obj关系的词语
        
        for objhandle in objhandles:# 将有nmod关系的词语保留进入句中
            nmodhandles:List[Edge] = [e for e in nmods if objhandle.target_index == e.target_index or objhandle.target_index == e.src_index]
            for nmodhandle in nmodhandles:
                if nmodhandle.src_index > range1[1]:
                    range1[1] = nmodhandle.src_index
                if nmodhandle.target_index > range1[1]:
                    range1[1] = nmodhandle.target_index

        singal_words = []
        for i in range(range1[0],range2[0]):
            token = tokens[i]
            if "W" in token.pos or "," in token.pos:
                for objhandle in objhandles:
                    if i == objhandle.src_index or i == objhandle.target_index:
                        singal_words.append(token.word)   
                continue
            else:
                singal_words.append(token.word)
        for i in range(range2[1],range1[1]+1):
            token = tokens[i]
            if "W" in token.pos or "," in token.pos:
                for objhandle in objhandles:
                    if i == objhandle.src_index or i == objhandle.target_index:
                        singal_words.append(token.word)   
                continue
            else:
                singal_words.append(token.word)

        part1 = (" ".join(singal_words)).replace(" '", "'") # 将句子从source到target输出
        part1 = part1.capitalize()
        keywords = [ifdep.target_word, ifdep.src_word]
        to_return.append(Type_Sentence(keywords, part1, range1, id))# 输出句中所有词语及其标记tag作为Keywords
        id += 1
    return [r for r in to_return if r is not None]