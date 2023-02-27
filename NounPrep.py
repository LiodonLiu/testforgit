## ?对于compund名词（ice cream）的处理发生问题？

from asyncio.windows_events import NULL
from stanza.server import CoreNLPClient
import language_tool_python
tool = language_tool_python.LanguageTool('en-US')

def extraction(ann):
    token_word: dict = {} # token:word对应字典
    deps_compound: list = [] # 这些变量的意义见参考文档 Annotators.docx
    deps_nmodof: list = []
    word_pos: list = []
    searching_texts:list = []
    all_texts:list = []
    dep_list: list = []
    prep_compound: list = []
    prep_list: list = []
    prep_list = ["in front of","beneath","in the middle of","before","around","behind",'inside','near','on','under']
    rela_obj: dict = {} # 关系为 obj 的两个词的字典，为了应对 obl:** 形式的介词关系
    usedwords: list = []
    result: list = []
    source_obl: list = []

    for prep in prep_list:
        dep_list.append("nmod:" + prep.replace(" ","_"))
        dep_list.append("obl:" + prep.replace(" ","_"))

    for sentence in ann.sentence:      # obl
        for edge in sentence.enhancedPlusPlusDependencies.edge: 
            if(edge.dep in dep_list):
                if("obl" in edge.dep):
                    source_obl.append(edge.source)

    for sentence in ann.sentence:
        token_offset_begin: int = int(sentence.tokenOffsetBegin)
        print("token_offset_begin: " + str(token_offset_begin))
        for token in sentence.token:
            token_word[token.tokenBeginIndex] = token.word
            word_pos.append([token.tokenBeginIndex,token.pos])
        for edge in sentence.enhancedPlusPlusDependencies.edge:  # coumpound
            if(edge.dep=='compound'):
                deps_compound.append([edge.source,edge.target])
            if(edge.dep=='nmod:of'):
                deps_nmodof.append([edge.source,edge.target])

        for edge in sentence.enhancedPlusPlusDependencies.edge:  # obj?
            if(edge.dep == "obj"):
                if(edge.source in source_obl):
                    rela_obj[edge.source] = edge.target
            print("————————rela_obj:————————")
            print(rela_obj)

    for token in word_pos:                                                # compound
        if(token[1] in ["NN","NNS"]):
            for edge in deps_compound:
                if(token[0] == edge[1]-1):
                    if(edge[0]>edge[1]):
                        searching_texts.append(token_word[edge[1]-1] + " " + token_word[edge[0]-1]) # 只考虑了 A-B和B-A 类型的compund关系，应该还会有A1-A1-B
                    else:
                        searching_texts.append(token_word[edge[0]-1] + " " + token_word[edge[1]-1])
            for i in deps_compound:
                for j in i:
                    usedwords.append(j-1)
            if(token[0] not in usedwords):
                    searching_texts.append(token_word[token[0]])
    print("————————searching_text:————————")
    print(searching_texts)
    all_texts = searching_texts[:]

    for sentence in ann.sentence:
        for edge in sentence.enhancedPlusPlusDependencies.edge:               # prep
                if(edge.dep in dep_list):
                    if("nmod" in edge.dep):  # nmod关系
                        dep = edge.dep.replace("nmod:","").replace("_"," ")

                        source = token_word[edge.source-1]
                        target = token_word[edge.target-1]

                        for deps in deps_compound: # 如果存在，则将prep关系的名词替换为其compound的整体
                            if(edge.source in deps):
                                source = token_word[deps[1]-1] + " " + token_word[deps[0]-1]
                            if(edge.target in deps):
                                target = token_word[deps[1]-1] + " " + token_word[deps[0]-1]

                        searching_texts.remove(source)
                        searching_texts.remove(target)

                        prep_compound.append([source,target,dep])
                        usedwords.append(edge.source-1)
                        usedwords.append(edge.target-1)
                    if("obl" in edge.dep):    # obl关系
                        dep = edge.dep.replace("obl:","").replace("_"," ")

                        for deps in deps_compound: # 如果存在，则将prep关系的名词替换为其compound的整体，有一点bug，目前先
                            if(rela_obj[edge.source] in deps):
                                source = token_word[deps[1]-1] + " " + token_word[deps[0]-1]
                                searching_texts.remove(source)
                            else:
                                source = NULL
                            if(edge.target in deps):
                                target = token_word[deps[1]-1] + " " + token_word[deps[0]-1]
                                searching_texts.remove(target)
                            else:
                                target = token_word[edge.target-1]
                            
                            if(source is not NULL):
                                prep_compound.append([source,target,dep])
                                usedwords.append(edge.source-1)
                                usedwords.append(edge.target-1)


    # in front of 中front因为词性为NN，会被认为是 residual_noun

    result = [prep_compound,searching_texts,all_texts]   # <== 形式 
    print("————————result:————————")
    return result


if __name__ == "__main__":
    input_text = "I found an ice cream in front of the door, and I like ice cream."
    ann = None
    with CoreNLPClient(
            # annotators=['tokenize','ssplit','pos','lemma','ner', 'parse', 'depparse','coref', 'openie'],
            annotators=['tokenize','ssplit','pos','depparse'],
            timeout=30000,
            memory='4G') as client:
        ann = client.annotate(input_text)

    result = extraction(ann)
    prep_compound = result[0]
    residual_nounce = result[1]
    print(result)