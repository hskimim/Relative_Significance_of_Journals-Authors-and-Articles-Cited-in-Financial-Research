import os
import oop_func as func
import personal_pkg as ref
import os
import re
from collections import Counter
import pandas as pd

def extract_the_file_path_under_year(year):
    root_ls = "../../paper_list/"
    root_ls = [root_ls + i for i in os.listdir("../../paper_list/") if re.search('[가-힣]',i)]
    process_ls = [os.listdir(i+'/{}'.format(year)) for i in root_ls]
    process_ls = [[root_ls[idx] + '/{}/'.format(year) + j for j in i] for idx,i in enumerate(process_ls)]
    return [j for i in process_ls for j in i]

def journal_txt_ls(journal,format_='txt'):
    '''
    HOW TO USE :
    ___________________________________________
    fm_txt_ls = journal_txt_ls('한국재무관리학회')
    sc_txt_ls = journal_txt_ls('한국증권학회지')
    dr_txt_ls = journal_txt_ls('한국파생상품학회')
    f_txt_ls = journal_txt_ls('한국재무학회')
    ___________________________________________
    '''
    root_ls = "../../paper_list/{}/".format(journal)
    journal_txt_ls = []

    file_path = sorted([root_ls + i for i in os.listdir(root_ls) if '20' in i.split("/")[-1]])
    for file in file_path :
        file_path = [file + '/' + i for i in os.listdir(file)]
        journal_txt_ls.append(file_path)
    return [j for i in journal_txt_ls for j in i if '{}'.format(format_) in j]

def split_to_sent(file_path,special_case=False):
    '''
    HOW TO USE :
    ___________________________________________________

    fm_sent_ls , fm_error_ls = split_to_sent(fm_path)
    f_sent_ls , f_error_ls = split_to_sent(f_path)
    sc_sent_ls , sc_error_ls = split_to_sent(sc_path)
    dr_sent_ls , dr_error_ls = split_to_sent(dr_path)
    _________________________________________________
    '''
    sent_refer_ls = []
    error_ls = []
    if not special_case :
        for idx,path in enumerate(file_path) :
            if idx % 100 ==0 : print(idx)
            try :
                ca = func.Slicing_paper(path,special_case=False)
                sent_refer_ls.append(ca.split())
                sent_refer_ls[-1] = list(zip(sent_refer_ls[-1],[str(path) for _ in range(len(sent_refer_ls[-1]))]))
            except Exception as e: error_ls.append((e,path))

        # sent_ls = [j[0] for i in sent_refer_ls for j in i]
        # path_ls = [j[1] for i in sent_refer_ls for j in i]
        return [j for i in sent_refer_ls for j in i] , error_ls
    else :
        for path in file_path :
            try :
                ca = func.Slicing_paper(path,special_case=True)
                sent_refer_ls.append(ca.split())
                sent_refer_ls[-1] = list(zip(sent_refer_ls[-1],[str(path) for _ in range(len(sent_refer_ls[-1]))]))
            except Exception as e: error_ls.append((e,path))

        # sent_ls = [j[0] for i in sent_refer_ls for j in i]
        # path_ls = [j[1] for i in sent_refer_ls for j in i]
        # return  sent_ls , path_ls , error_ls
        return [j for i in sent_refer_ls for j in i] , error_ls

def fix_the_error_file(error_path_ls):
    file_ = []
    valueerror_ls = []
    unicodeerror_ls = []
    sentences_ls = []
    err_cnt = 0

    for i in error_path_ls :
        for j in os.listdir("error_solved_file/") :
            if i.split('/')[-1] in j :
                file_.append("error_solved_file/" + j)
    for path in file_ :
        try :
            process1 = func.Slicing_paper(path,special_case=False)
            sentences_ls.append(process1.split())
            sentences_ls[-1] = list(zip(sentences_ls[-1],[str(path) for _ in range(len(sentences_ls[-1]))]))

        except ValueError :
            valueerror_ls.append(path)

    for idx,file in enumerate(valueerror_ls) :
        try :
            process1 = func.Slicing_paper(file,special_case=True)
            sentences_ls.append(process1.split())
            sentences_ls[-1] = list(zip(sentences_ls[-1],[str(path) for _ in range(len(sentences_ls[-1]))]))
        except :
            err_cnt +=1

    # sent_ls = [j[0] for i in sentences_ls for j in i]
    # path_ls = [j[1] for i in sentences_ls for j in i]
    print('The number of original error files was {}, but it was reduced to {}.'.format(len(error_path_ls),len(file_)-err_cnt))
    print('The Number of final error file is {}'.format(err_cnt))
    print('The length of sentences which I fixed the error is {}'.format(len(sentences_ls)))
    # return sent_ls , path_ls
    return [j for i in sentences_ls for j in i]

def show_quote_and_unquote(sent_ls):
    perfect_sent = [i for i in sent_ls if re.search("“.+”",i[0])]
    imperfect_sent = [i for i in sent_ls if not re.search("“.+”",i[0])]
    print('ratio of double quotation line : {}'.format(len(perfect_sent) / len([i for i in sent_ls])))
    print('total length of double quote lines: {}'.format(len(perfect_sent)))
    print('total length of lines: {}'.format(len(sent_ls)))

    return perfect_sent , imperfect_sent

def make_dictionary(quote_sent,quote_format_head = "“",quote_format_tail = "”") :
    paper_ls = [re.findall('{}.+{}'.format(quote_format_head,quote_format_tail),i[0])[0] if re.findall('{}.+{}'.format(quote_format_head,quote_format_tail),i[0]) else None for i in quote_sent]
    journal_ls = [re.findall('{}.+'.format(quote_format_tail),i[0])[0] if re.findall('{}.+'.format(quote_format_tail),i[0]) else None for i in quote_sent]
    author_ls = [re.findall('.+{}'.format(quote_format_head),i[0])[0] if re.findall('.+{}'.format(quote_format_head),i[0]) else None for i in quote_sent]
    year_ls = [re.findall("20[0-9]{2}|19[0-9]{2}",i[0])[0] if re.findall("20[0-9]{2}|19[0-9]{2}",i[0]) else None for i in quote_sent]
    abs_path_ls = [i[1] for i in quote_sent]

    author_ls = [i.replace('{}'.format(quote_format_head),'') if i else None for i in author_ls]
    journal_ls = [re.sub("20[0-9]{2}|19[0-9]{2}",'',i) if i else None for i in journal_ls]
    journal_ls = [re.sub("[()]",'',i) if i else None for i in journal_ls]
    paper_ls = [i[1:-1] for i in paper_ls]
    paper_ls = [i.strip() for i in paper_ls]

    df = pd.DataFrame(columns=['author','year','paper','journal'])
    df['author'] = author_ls
    df['year'] = year_ls
    df['paper'] = paper_ls
    df['journal'] = journal_ls
    df['refer_raw'] = [i[0] for i in quote_sent]
    citing_year_ls = [i[1].split("/")[-2] if re.search("20[0-9]{2}",i[1]) else i[1] for i in quote_sent]
    df['citing_year'] = citing_year_ls
    df['path'] = abs_path_ls
    print(df.shape )
    return df

def make_dictionary_under_journal(quote_sent) :
    paper_ls = [re.findall("“.+”",i)[0] if re.findall("“.+”",i) else None for i in quote_sent]
    journal_ls = [re.findall("”.+",i)[0] if re.findall("”.+",i) else None for i in quote_sent]
    author_ls = [re.findall(".+“",i)[0] if re.findall(".+“",i) else None for i in quote_sent]
    year_ls = [re.findall("20[0-9]{2}|19[0-9]{2}",i)[0] if re.findall("20[0-9]{2}|19[0-9]{2}",i) else None for i in quote_sent]

    author_ls = [i.replace('“','') if i else None for i in author_ls]
    journal_ls = [re.sub("20[0-9]{2}|19[0-9]{2}",'',i) if i else None for i in journal_ls]
    journal_ls = [re.sub("[()]",'',i) if i else None for i in journal_ls]
    paper_ls = [i[1:-1] for i in paper_ls]
    paper_ls = [i.strip() for i in paper_ls]

    fm_df = pd.DataFrame(columns=['author','year','paper','journal'])
    fm_df['author'] = author_ls
    fm_df['year'] = year_ls
    fm_df['paper'] = paper_ls
    fm_df['journal'] = journal_ls

    return fm_df

def make_imperfect_ls(imperfect_sent) :
    imperfect_ls = []
    path_ls = [i[1] for i in imperfect_sent]

    for idx in range(len(imperfect_sent)) :
        try :
            start_index = max([m.end() for m in re.finditer('[A-Z][.]',imperfect_sent[idx][0])]) + 1
        except : start_index = 0

        imperfect_ls.append(imperfect_sent[idx][0][start_index:])

    imperfect_ls = [i for i in imperfect_ls if re.search('[a-zA-Z가-힣]',i)]
    imperfect_ls = [i.replace('.','').replace('  ',' ').strip() for i in imperfect_ls]
    imperfect_ls = [i[:re.search('journal',i.lower()).start()] if re.search('journal',i.lower()) else i for i in imperfect_ls]
    return list(zip(imperfect_ls,path_ls))


def catch_the_paper_under_similarity_score(double_quote_dictionary,imperfect_ls,score=0.5) :
    '''
    Empirically, 0.9 score shows nice outcome.
    '''

    paper_under_similarity_score = []
    print('the length of dictionary is {}.. the cost of function is proportional with it'\
          .format(len(double_quote_dictionary)))
    for idx1 in range(len(double_quote_dictionary)) :
        if idx1 % 4000 == 0 : print(idx1)
        for idx2 in range(len(imperfect_ls)) :
            if re.search('20[0-9]{2}|19[0-9]{2}',imperfect_ls[idx2]) :
                dictionary_paper = [i for i in double_quote_dictionary['paper'][idx1].lower().split(' ') if i]
                imperpect_paper = [i for i in imperfect_ls[idx2].lower().split(" ") if i]

                similarity_score = \
                    len(set(dictionary_paper).intersection(imperpect_paper)) / len(dictionary_paper)
                if similarity_score > score and \
                double_quote_dictionary['year'][idx1] == re.findall('20[0-9]{2}|19[0-9]{2}',imperfect_ls[idx2])[0] :
                    paper_under_similarity_score.append((double_quote_dictionary['paper'][idx1],imperfect_ls[idx2]))
            else :
                similarity_score = \
                    len(set(dictionary_paper).intersection(imperpect_paper)) / len(dictionary_paper)
                if similarity_score == 1  :
                    paper_under_similarity_score.append((double_quote_dictionary['paper'][idx1],imperfect_ls[idx2]))
    return paper_under_similarity_score

def catch_the_paper_under_similarity_score_for_concurrent(zip_ls,score=0.9) :
    '''
    Empirically, 0.9 score shows nice outcome.
    '''
    double_quote_dictionary = zip_ls[0]
    imperfect_ls = zip_ls[1]

    paper_under_similarity_score = []
    print('the length of dictionary is {}.. the cost of function is proportional with it'\
          .format(len(double_quote_dictionary)))
    for idx1 in range(len(double_quote_dictionary)) :
        if idx1 % 4000 == 0 : print(idx1)
        for idx2 in range(len(imperfect_ls)) :
            if re.search('20[0-9]{2}|19[0-9]{2}',imperfect_ls[idx2]) :
                dictionary_paper = [i for i in double_quote_dictionary['paper'][idx1].lower().split(' ') if i]
                imperpect_paper = [i for i in imperfect_ls[idx2].lower().split(" ") if i]

                similarity_score = \
                    len(set(dictionary_paper).intersection(imperpect_paper)) / len(dictionary_paper)
                if similarity_score > score and \
                double_quote_dictionary['year'][idx1] == re.findall('20[0-9]{2}|19[0-9]{2}',imperfect_ls[idx2])[0] :
                    paper_under_similarity_score.append((double_quote_dictionary['paper'][idx1],imperfect_ls[idx2]))
            else :
                similarity_score = \
                    len(set(dictionary_paper).intersection(imperpect_paper)) / len(dictionary_paper)
                if similarity_score == 1  :
                    paper_under_similarity_score.append((double_quote_dictionary['paper'][idx1],imperfect_ls[idx2]))
    return paper_under_similarity_score


def concat_df_for_make_counter_df_per_journal(quote_ls,quote_df,catch_paper_name_ls) :
    dictionary = make_dictionary_under_journal(quote_ls)

    for idx in range(len(catch_paper_name_ls)) :
        if len(dictionary) % 1000 == 0 : print(len(dictionary))
        append_df = quote_df[quote_df['paper'] == catch_paper_name_ls[idx]]
        dictionary = pd.concat([dictionary,append_df])

    return dictionary

def tuning_the_journal_and_make_counter_df(dictionary) :

    tuning_ls = [','.join(re.findall('[a-zA-Z가-힣\s]',i)).replace(',','').lower() if i else None for i in dictionary['journal'].tolist()]
    tuning_ls = [i.replace('vol','').replace('no','').strip() if i else None for i in tuning_ls]
    tuning_ls = [i.replace('제권','').replace('제호','').replace(' 호','').strip() if i else None for i in tuning_ls]
    journal_counter_df = pd.DataFrame.from_dict(Counter(tuning_ls),orient='index',columns=['count']).sort_values('count',ascending=False)
    return journal_counter_df
