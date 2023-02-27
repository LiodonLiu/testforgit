from stanza.server import CoreNLPClient
from PIL import Image, ImageDraw, ImageFont
import random
import crawler
from enhancedDemoRefactored import Edge
from enhancedDemoRefactored import generate_type_sentences
from enhancedDemoRefactored import find_important_word
from typing import List
from typing import Tuple
import language_tool_python
tool = language_tool_python.LanguageTool('en-US')

input_text = '''It honestly depends how cold it is, because if it's too cold and there are a lot of clouds and it starts raining, then it could snow and you could go snowboarding.'''
input_text = tool.correct(input_text)
print("Corrected input text:")
print(input_text)


# 提供 Google Image Search 的 API 信息
# dev_api_key = 'AIzaSyA1_KidBaLn5j27aBz8BR0gg68_IafGfqw'
# project_cx = '648aff331d7b32a7a'

# 因未知原因无法使用
# project_cx = '1c1dc7279d62a82a3'
# dev_api_key = 'AIzaSyDHkSBckiZEyPHDU9B3r76vUSoUIR1ppg0'

# 提供 API 密匙以及程序 CX 运行许可
# gis = GoogleImagesSearch(dev_api_key, project_cx)

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
        my_edges.append(Edge(edge.dep, token_offset_begin + int(edge.source)-1, tokens[token_offset_begin+int(edge.source)-1].word, token_offset_begin + int(edge.target)-1, tokens[token_offset_begin+int(edge.target)-1].word))
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

### Combine enhanced++ stuff with open IE stuff
complete_info_phrases: List[Complete_Info_Phrase] = []
# format: ("if", "part1", keyword, part1, tokenRange, id)
# [0] can be "if" or "because", [1] can be "part1" or "part2", [2] and [3] are a corresponding keyword and sentence fragment

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
    _search_params = {
    'q': complete_info_phrases[i].keyword + ' clipart',
    'num': 1,
    'fileType': 'jpg', # was 'jpg|png'
    }
    _search_params=str(_search_params)
    img_filename = (complete_info_phrases[i].part_text + str(random.randint(0, 9999999))).replace("'", "")
    # gis.search(search_params=_search_params, path_to_dir='foundImages/', width=500, height=500, custom_image_name=img_filename)
    crawler.use(key_word_=complete_info_phrases[i].keyword,dest_folder_='H:/VS Code/AI Viz/AllCodeAndFiles/foundImages',num_image_=4,nthread_=8, file_name_=img_filename)
    new_phrases_obj[i] = (complete_info_phrases[i].keyword, complete_info_phrases[i].part_text, img_filename)

print(str(new_phrases_obj))

#### Creating final image ####

word_font = ImageFont.truetype('H:/VS Code/AI Viz/Arial.ttf', 40)
    
canvas_width = (len(new_phrases_obj)*800)
canvas_height = 900
canvas_img = Image.new('RGB', (canvas_width, canvas_height), color=(255, 255, 255))

x_offset = 150
y_offset = 125
counter = 0
stagger = 50

for phrase in new_phrases_obj:
    try:
        img = Image.open('H:/VS Code/AI Viz/AllCodeAndFiles/foundImages/' + phrase[2] + '.jpg')
        img = img.resize((500, 500))
        canvas_img.paste(img, (x_offset, y_offset))
        d = ImageDraw.Draw(canvas_img)
        d.text((x_offset, y_offset+600+stagger), phrase[1], font=word_font, fill=(50, 50, 50))
        x_offset += 800
        counter += 1
        stagger *= -1
    except Exception as e:
        print("Img error " + str(e))
    
canvas_img.save('final_canvas.jpg')
    
print("Done")
    
#### Remove exact duplicates and object duplicates, then reduce to max_phrases total phrases ####
