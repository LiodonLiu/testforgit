from stanza.server import CoreNLPClient
import os
from PIL import Image, ImageDraw, ImageFont
import random
import bbid
from NounPrep import extraction
from changewhite import change
from enhancedDemoRefactored import Edge
from enhancedDemoRefactored import generate_type_sentences
from enhancedDemoRefactored import find_important_word
from infrontof import before
from behind import behind
from inside import inside
from around import around
from on import on
from under import under
from near import near
from typing import List
from typing import Tuple
import language_tool_python

def locate(input_text):
    tool = language_tool_python.LanguageTool('en-US')
    myflag = 0
    # input_text = "I found an ice cream near the door, and a monkey on the house."
    input_text = tool.correct(input_text) 
    print("Corrected input text:")
    print(input_text)
    # format: ("if", "part1", keyword, part1, id)
    class Complete_Info_Phrase:
        def __init__(self, type: str, part_num: int, keyword: str, part_text: str, part_range: Tuple[int], id: int):
            self.type: str = type
            self.part_num: int = part_num
            self.keyword: str = keyword
            self.part_text: str = part_text
            self.part_range: Tuple[int] = part_range
            self.id: int = id

    openie_key_phrases = []

    ann = None
    with CoreNLPClient(
            # annotators=['tokenize','ssplit','pos','lemma','ner', 'parse', 'depparse','coref', 'openie'],
            annotators=['depparse', 'openie'],
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
            my_edges.append(Edge(edge.dep, token_offset_begin + int(edge.source)-1,
            tokens[token_offset_begin+int(edge.source)-1].word, token_offset_begin + int(edge.target)-1, 
            tokens[token_offset_begin+int(edge.target)-1].word))
        for trip in sentence.openieTriple:
            openie_key_phrases.append((trip.object, trip.subject + ' ' + trip.relation + ' ' + trip.object, ''))
    print(my_edges)

    ### Refine open IE key phrases
    max_phrases = 5
    openie_key_phrases = list(set(openie_key_phrases))
    reduced_key_phrases = []
    for phrase in openie_key_phrases:
        duplicate = False
        for r_phrase in reduced_key_phrases:
            if phrase[0] in r_phrase[0] or r_phrase[0] in phrase[0] or r_phrase[0] == phrase[0]:
                duplicate = True
        if not duplicate:
            reduced_key_phrases.append(phrase)

    if len(reduced_key_phrases) > max_phrases:
        phrases_to_keep = []
        for i in range(0, max_phrases):
            rInt = random.randint(0, len(reduced_key_phrases) - 1)
            while rInt in phrases_to_keep:
                rInt = random.randint(0, len(reduced_key_phrases))
            phrases_to_keep.append(rInt)

        openie_key_phrases = []
        for index in phrases_to_keep:
            if index < len(reduced_key_phrases):
                openie_key_phrases.append(reduced_key_phrases[index])
    else:
        openie_key_phrases = reduced_key_phrases

    ### Output enhanced++ dependency sentences
    resultsIf = generate_type_sentences(tokens, my_edges, "if")
    for result in resultsIf:
        print("Keywords: " + result.keywords[0] + ", " + result.keywords[1])
        print("Sentence: If " + result.parts_text[0] + " then " + result.parts_text[1] + ".")

    resultsBecause = generate_type_sentences(tokens, my_edges, "because")
    for result in resultsBecause:
        print("Keywords: " + result.keywords[0] + ", " + result.keywords[1])
        print("Sentence: " + result.parts_text[1] + " because " + result.parts_text[0] + ".")

    if resultsIf == []:
        if resultsBecause == []:
            myflag = 1
            result = extraction(ann)
            resultsBoundpiece = result[0]
            resultsElsepiece = result[1]
            results = result[2]

    if myflag == 0:
        ### Combine enhanced++ stuff with open IE stuff
        complete_info_phrases: List[Complete_Info_Phrase] = []

        for phrase in openie_key_phrases:
            for result in resultsIf:
                for part in [0, 1]:
                    keyword = ""
                    if phrase[0] in result.parts_text[part]: # found open ie keyword in if part1
                        keyword = phrase[0]
                    else:
                        keyword = find_important_word(result.part_ranges[part], ann)[0]
                    complete_info_phrases.append(Complete_Info_Phrase("if", part, keyword, result.parts_text[part], result.part_ranges[part], result.id))
            for result in resultsBecause:
                for part in [0, 1]:
                    keyword = ""
                    if phrase[0] in result.parts_text[part]: # found open ie keyword in if part1
                        keyword = phrase[0]
                    else:
                        keyword = find_important_word(result.part_ranges[part], ann)[0]
                    complete_info_phrases.append(Complete_Info_Phrase("because", part, keyword, result.parts_text[part], result.part_ranges[part], result.id))

        ### Conslidate to one tuple per id
        complete_info_phrases_dupl: List[Complete_Info_Phrase] = []
        for phr in complete_info_phrases:
            already_added = False
            for phr_dupl in complete_info_phrases_dupl:
                if phr_dupl.id == phr.id and phr_dupl.type == phr.type and phr_dupl.part_num == phr.part_num:
                    already_added = True
                    break
            if not already_added:
                complete_info_phrases_dupl.append(phr)
        complete_info_phrases = complete_info_phrases_dupl

        ### Generate images for enhanced++ sentences
        new_phrases_obj = [None] * len(complete_info_phrases)

        for i in range(len(complete_info_phrases)):
            img_filename = (complete_info_phrases[i].part_text).replace("'", "")
            if os.path.exists('./foundImages/' + img_filename + '.jpg') is False:
                bbid.use(search_string_=complete_info_phrases[i].part_text + ' emoji' + ' clipart', output_='./foundImages', filename_ = img_filename)
            new_phrases_obj[i] = (complete_info_phrases[i].keyword, complete_info_phrases[i].part_text, img_filename)

        print(str(new_phrases_obj))

        #### Creating final image ####

        word_font = ImageFont.truetype('./font/Arial.ttf', 40)
            
        canvas_width = (len(new_phrases_obj)*800)
        canvas_height = 900
        canvas_img = Image.new('RGB', (canvas_width, canvas_height), color=(255, 255, 255))

        x_offset = 150
        y_offset = 125
        counter = 0
        stagger = 50

        for phrase in new_phrases_obj:
            try:
                img = Image.open('./foundImages/' + phrase[2] + '.jpg')
                img = img.resize((500, 500))
                canvas_img.paste(img, (x_offset, y_offset))
                d = ImageDraw.Draw(canvas_img)
                d.text((x_offset, y_offset+550), phrase[1], font=word_font, fill=(50, 50, 50))
                x_offset += 800
                counter += 1
            except Exception as e:
                print("Img error " + str(e))
            
        canvas_img.save('final_canvas.jpg')
            
        print("Done")

    else:
        #首先提取句中所有名词，统一爬取对应图片，以防介词名词图像生成时受阻
        for i in range(len(results)):
            img_filename = (results[i]).replace("'", "")
            if os.path.exists('./foundImages/' + img_filename + '.jpg') is False:
                bbid.use(search_string_=results[i] + ' emoji' + ' clipart', output_='./foundImages', filename_ = img_filename)
            change('./foundImages/' + img_filename + '.jpg') #将RGBA与杂色背景的RGB图片更改为白色背景的RGB图片

        #开始计算画布长度
        canvas_width = 0
        step = 0
        #开始生成介词名词图片
        Boundlength = len(resultsBoundpiece)
        Elselength = len(resultsElsepiece)
        new_phrases_obj = [None] * (Boundlength + Elselength)
        for i in range(Boundlength):
            if resultsBoundpiece[i][2] == "before" or resultsBoundpiece[i][2] == "in front of":
                step = 800
                before(resultsBoundpiece[i][0],resultsBoundpiece[i][1],resultsBoundpiece[i][2])
            elif resultsBoundpiece[i][2] == "behind":
                step = 800
                behind(resultsBoundpiece[i][0],resultsBoundpiece[i][1],resultsBoundpiece[i][2])
            elif resultsBoundpiece[i][2] == "in":
                step = 800
                inside(resultsBoundpiece[i][0],resultsBoundpiece[i][1],resultsBoundpiece[i][2])
            elif resultsBoundpiece[i][2] == "around":
                step = 1800
                around(resultsBoundpiece[i][0],resultsBoundpiece[i][1],resultsBoundpiece[i][2])
            elif resultsBoundpiece[i][2] == "on" or resultsBoundpiece[i][2] == "over" or resultsBoundpiece[i][2] == "above":
                step = 800
                on(resultsBoundpiece[i][0],resultsBoundpiece[i][1],resultsBoundpiece[i][2])
            elif resultsBoundpiece[i][2] == "under" or resultsBoundpiece[i][2] == "beneath" or resultsBoundpiece[i][2] == "below":
                step = 800
                under(resultsBoundpiece[i][0],resultsBoundpiece[i][1],resultsBoundpiece[i][2])
            elif resultsBoundpiece[i][2] == "near" or resultsBoundpiece[i][2] == "by" or resultsBoundpiece[i][2] == "beside" or resultsBoundpiece[i][2] == "next to" or resultsElsepiece[i][2] == "left" or resultsElsepiece[i][2] == "right":
                step = 1300
                near(resultsBoundpiece[i][0],resultsBoundpiece[i][1],resultsBoundpiece[i][2])

            canvas_width += step
            # resultsElse.append(resultsElsepiece[i][0]+" "+resultsElsepiece[i][2]+" "+resultsElsepiece[i][1])
            img_filename = (resultsBoundpiece[i][0]+" "+resultsBoundpiece[i][2]+" "+resultsBoundpiece[i][1]).replace("'", "")
            new_phrases_obj[i] = (resultsBoundpiece[i][0]+" "+resultsBoundpiece[i][2]+" "+resultsBoundpiece[i][1], img_filename, step)

        for i in range(Elselength):
            canvas_width += 800
            img_filename = (resultsElsepiece[i]).replace("'", "")
            new_phrases_obj[i + Boundlength] = (resultsElsepiece[i], img_filename, 800)

        print(str(new_phrases_obj))

        #### Creating final image ####

        word_font = ImageFont.truetype('./font/Arial.ttf', 40)

        ##首先生成生成图的画布，若是考虑位置关系的话，画布大小需要更改    
        canvas_height = 1800
        canvas_img = Image.new('RGB', (canvas_width, canvas_height), color=(255, 255, 255))

        # x_offset = 125
        # y_offset = 125
        x_offset = 0
        y_offset = 0

        for i in range(Boundlength):
            try:
                img = Image.open('./foundImages/' + new_phrases_obj[i][1] + '.jpg')
                # img = img.resize((500, 500))               #调整图片大小
                canvas_img.paste(img, (x_offset, y_offset))#在画布上输出图片
                # d = ImageDraw.Draw(canvas_img)             #在图片下方显示对应的图片名
                # d.text((x_offset, y_offset+550), phrase[1], font=word_font, fill=(50, 50, 50))
                x_offset += new_phrases_obj[i][2]
            except Exception as e:
                print("Img error " + str(e))

        y_offset = 650
        for i in range(Elselength):
            try:
                img = Image.open('./foundImages/' + new_phrases_obj[i + Boundlength][1] + '.jpg')
                img = img.resize((500, 500))               #调整图片大小
                canvas_img.paste(img, (x_offset + 150, y_offset))#在画布上输出图片
                d = ImageDraw.Draw(canvas_img)             #在图片下方显示对应的图片名
                d.text((x_offset + 150, 1700), new_phrases_obj[i + Boundlength][1], font=word_font, fill=(50, 50, 50))
                x_offset += new_phrases_obj[i + Boundlength][2]
            except Exception as e:
                print("Img error " + str(e))

        d = ImageDraw.Draw(canvas_img)             #在图片下方显示对应的图片名
        d.text((150, 1750), input_text, font=word_font, fill=(50, 50, 50))
        canvas_img.save('final_canvas.jpg')

        print("Done")

        #### Remove exact duplicates and object duplicates, then reduce to max_phrases total phrases ####

if __name__ == "__main__":
    input_text = "I found an ice cream near the door, and a monkey on the house."
    locate(input_text)