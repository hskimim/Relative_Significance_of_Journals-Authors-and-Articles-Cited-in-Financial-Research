import os
import oop_func as func
import personal_pkg as ref
import os
import re
from collections import Counter
import pandas as pd

def journal_txt_ls(journal):
    '''
    HOW TO USE :
    ___________________________________________
    fm_txt_ls = journal_txt_ls('한국재무관리학회')
    sc_txt_ls = journal_txt_ls('한국증권학회지')
    dr_txt_ls = journal_txt_ls('한국파생상품학회')
    f_txt_ls = journal_txt_ls('한국재무학회')
    ___________________________________________
    '''
    file_path = \
    sorted(['../../paper_list/{}/'.format(journal) + i for i in [i for i in os.listdir('../../paper_list/{}/'.format(journal)) if '20' in i]])

    journal_txt_ls = []

    for year,i in enumerate([os.listdir(i) for i in file_path]) :
        txt_ls = []
        for j in i :
            if 'txt' in j :
                txt_ls.append(file_path[year] +'/'+ j)
        journal_txt_ls.append(txt_ls)

    return journal_txt_ls

def split_to_sent(file_path):
    '''
    HOW TO USE :
    ___________________________________________________
    fm_path = [refer for i in fm_txt_ls for refer in i]
    f_path = [refer for i in f_txt_ls for refer in i]
    sc_path = [refer for i in sc_txt_ls for refer in i]
    dr_path = [refer for i in dr_txt_ls for refer in i]

    fm_sent_ls , fm_error_ls = split_to_sent(fm_path)
    f_sent_ls , f_error_ls = split_to_sent(f_path)
    sc_sent_ls , sc_error_ls = split_to_sent(sc_path)
    dr_sent_ls , dr_error_ls = split_to_sent(dr_path)
    _________________________________________________
    '''
    sent_refer_ls = []
    error_ls = []

    for path in file_path :
        try :
            ca = func.Slicing_paper(path)
            sent_refer_ls.append(ca.split())
        except Exception as e: error_ls.append((e,path))

    return [j for i in sent_refer_ls for j in i] , error_ls

def show_quote_and_unquote(sent_ls):
    perfect_sent = [i for i in sent_ls if re.search("“.+”",i)]
    imperfect_sent = [i for i in sent_ls if not re.search("“.+”",i)]
    print('ratio of double quotation line : {}'.format(len(perfect_sent) / len([i for i in sent_ls])))
    print('total length of double quote lines: {}'.format(len(perfect_sent)))
    print('total length of lines: {}'.format(len(sent_ls)))

    return perfect_sent , imperfect_sent

def make_dictionary(quote_sent) :
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

    print('eliminate the duplicated paper name')
    print(fm_df.shape )

    idx_ls = []

    for idx,val in enumerate(fm_df['paper'].tolist()) :
        if val not in [i[1] for i in idx_ls] :
            idx_ls.append((idx,val))

    fm_df = fm_df.iloc[[i[0] for i in idx_ls]]
    fm_df.reset_index(inplace=True)
    print(fm_df.shape )

    return fm_df

def make_imperfect_ls(imperfect_sent) :
    imperfect_ls = []

    for idx in range(len(imperfect_sent)) :
        try :
            start_index = max([m.end() for m in re.finditer('[A-Z][.]',imperfect_sent[idx])]) + 1
        except : start_index = 0

        imperfect_ls.append(imperfect_sent[idx][start_index:])

    imperfect_ls = [i for i in imperfect_ls if re.search('[a-zA-Z가-힣]',i)]
    imperfect_ls = [i.replace('.','').replace('  ',' ').strip() for i in imperfect_ls]
    imperfect_ls = [i[:re.search('journal',i.lower()).start()] if re.search('journal',i.lower()) else i for i in imperfect_ls]
    return imperfect_ls


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


    return paper_under_similarity_score
