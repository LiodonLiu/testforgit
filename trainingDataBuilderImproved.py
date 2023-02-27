import csv
from stanza.server import CoreNLPClient
from enhancedDemoRefactored import token_index_to_word
from enhancedDemoRefactored import find_num_connections_list
from enhancedDemoRefactored import find_pos_list
from enhancedDemoRefactored import find_epp_connection_list
from enhancedDemoRefactored import get_total_token_amt
from enhancedDemoRefactored import get_token_list

def validate_data(csv_file):
    reader: csv.DictReader = csv.DictReader(csv_file)

    for line in reader:
        ann = None
        with CoreNLPClient(
                # annotators=['tokenize','ssplit','pos','lemma','ner', 'parse', 'depparse','coref', 'openie'],
                annotators=['depparse'],
                timeout=30000,
                memory='4G') as client:
            ann = client.annotate(line['text'])
        found_phrases = []
        for _tok_range in line['target_ranges'].split('|'):
            phrase = ""
            x: int = -1
            y: int = -1
            tok_range = _tok_range.strip()
            if len(tok_range.split(' ')) > 1:
                x = int(tok_range.split(' ')[0])
                y = int(tok_range.split(' ')[1])
            elif len(tok_range.split(' ')) == 1:
                x = int(tok_range)
                y = int(tok_range)
            else:
                print("Less than one range value?")
            for _token_ind in range(x, y+1):
                token_ind = _token_ind - 1
                result = token_index_to_word(token_ind, ann)
                phrase += result[0] + " "
                print("Phrase is now: " + phrase + " from result " + str(result))
            found_phrases.append(phrase.strip().replace(" '", "'"))
        for i in range(0, len(line['target_ranges'].split('|'))):
            real_phrase = line['target_phrases'].split('|')[i].strip()
            if real_phrase != found_phrases[i]:
                print("Validation Error: " + real_phrase + " != " + found_phrases[i] + " at index " + str(i))
                
def build_training_data():
    with open('dataSourceImproved.csv', 'r') as orig_csv:
        # validate_data(orig_csv)
        reader: csv.DictReader = csv.DictReader(orig_csv)
        
        with open('updatedTrainingDataImproved.csv', 'w') as new_csv:
            # field_names are [id	question	text	token_amt	tokens_all	token_rank	target_phrases	target_ranges	num_epp_connections_all	all_edges	epp_connections_all	pos_all	all_pairs	pair_num_epp]
            writer: csv.DictWriter = csv.DictWriter(new_csv, fieldnames=reader.fieldnames)
            writer.writeheader()

            for line in reader:
                ann = None
                with CoreNLPClient(
                        # annotators=['tokenize','ssplit','pos','lemma','ner', 'parse', 'depparse','coref', 'openie'],
                        annotators=['depparse'],
                        timeout=30000,
                        memory='4G') as client:
                    ann = client.annotate(line['text'])
                
                total_token_amt = get_total_token_amt(ann)
                
                token_ranking = find_num_connections_list(ann)
                pos_list = find_pos_list(ann)
                epp_connection_list = find_epp_connection_list(ann)
                token_list = get_token_list(ann)
                
                num_epp_connections_all = ''
                epp_connections_all = ''
                all_edges = ''
                all_pos = ''
                all_tokens = ''
                
                #for _tok_range in line['target_ranges'].split('|'):
                tok_range = [1, total_token_amt]
                x: int = tok_range[0]
                y: int = tok_range[1]
                
                these_nums = ''
                this_epp_connection = ''
                this_pos = ''
                these_tokens = ''
                for i in range(x, y+1):
                    these_nums += str(token_ranking[i-1]) + " "
                    this_epp_connection += epp_connection_list[i-1] + " "
                    this_pos += pos_list[i-1] + " "
                    these_tokens += token_list[i-1] + " "
                num_epp_connections_all += these_nums.strip()
                epp_connections_all += this_epp_connection.strip()
                all_pos += this_pos.strip()
                all_tokens += these_tokens.strip()
                
                new_line = line
                new_line['num_epp_connections_all'] = num_epp_connections_all
                new_line['epp_connections_all'] = epp_connections_all.replace(";|", "|").replace("; ", " ")
                new_line['pos_all'] = all_pos
                new_line['token_amt'] = total_token_amt
                new_line['tokens_all'] = all_tokens
                writer.writerow(new_line)

def build_numeric_training_data():
    
    eppDepDict = {"testEntry": "hi"}
    with open('eppDepDict.csv') as eppDepDict_file:
        eppDict_reader: csv.DictReader = csv.DictReader(eppDepDict_file)
        field_names = eppDict_reader.fieldnames
        for line in eppDict_reader:
            for field_name in field_names:
                eppDepDict[field_name] = line[field_name]
    print(str(eppDepDict))
    
    posDict = {"testEntry": "hi"}
    with open('posDict.csv') as posDict_file:
        eppDict_reader: csv.DictReader = csv.DictReader(posDict_file)
        field_names = eppDict_reader.fieldnames
        for line in eppDict_reader:
            for field_name in field_names:
               posDict[field_name] = line[field_name]
    print(str(posDict))
    
    with open('updatedTrainingDataImproved.csv', 'r') as train_data_bad:
        # field_names are [id	question	text	token_amt	tokens_all	token_rank	target_phrases	target_ranges	num_epp_connections_all	all_edges	epp_connections_all	pos_all	all_pairs	pair_num_epp]
        reader: csv.DictReader = csv.DictReader(train_data_bad)
        
        with open('numeric_updatedTrainingDataImproved.csv', 'w') as train_data_numeric:
            # field_names are [id	question	text	token_amt	tokens_all	token_rank	target_phrases	target_ranges	num_epp_connections_all	all_edges	epp_connections_all	pos_all	all_pairs	pair_num_epp]
            writer: csv.DictWriter = csv.DictWriter(train_data_numeric, fieldnames=reader.fieldnames)
            writer.writeheader()
            
            for line in reader:
                #print("New line in regular data")
                new_line = line
                
                epp_connections_all = ''
                for word_deps in line["epp_connections_all"].split(';'):
                    #print("New word deps")
                    new_word_dep = ''
                    for dep in word_deps.split(' '):
                        new_pos = ''
                        if dep in eppDepDict:
                            new_pos = eppDepDict[dep] 
                            new_word_dep += new_pos + " "
                        else:
                            pass  # TODO: check if dict_line actually has dep; if it doesn't then add it
                    epp_connections_all += new_word_dep.strip() + ";"
                new_line['epp_connections_all'] = epp_connections_all
                
                pos_all = ''
                for pos in line["pos_all"].split(' '):
                    new_pos = ''
                    if pos in posDict:
                        new_pos = posDict[pos]
                    else:
                        pass  # TODO: check if dict_line actually has dep; if it doesn't then add it
                    pos_all += new_pos.strip() + " "
                new_line['pos_all'] = pos_all
                
                
                writer.writerow(new_line)

    
    
if __name__ == "__main__":
    #build_training_data()
    build_numeric_training_data()
    print("Done")
