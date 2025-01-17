import io
import re
import pandas as pd
import numpy as np
from IPython.display import display , Markdown

from pdfminer.converter import TextConverter
from pdfminer.pdfinterp import PDFPageInterpreter
from pdfminer.pdfinterp import PDFResourceManager
from pdfminer.pdfpage import PDFPage
import warnings
# read pdf file
def extract_text_from_pdf(pdf_path):
    '''
    read pdf file into string type
    '''
    resource_manager = PDFResourceManager()
    fake_file_handle = io.StringIO()
    converter = TextConverter(resource_manager, fake_file_handle)
    page_interpreter = PDFPageInterpreter(resource_manager, converter)

    with open(pdf_path, 'rb') as fh:
        for page in PDFPage.get_pages(fh,
                                      caching=True,
                                      check_extractable=True):
            page_interpreter.process_page(page)

        text = fake_file_handle.getvalue()

    # close open handles
    converter.close()
    fake_file_handle.close()

    if text:
        return text

def extract_text_from_txt(path):
    with open(path,'rt') as f :
        lines = f.readlines()
    # return ','.join(lines).replace('\n','')
    return ','.join(lines)

def extract_text_from_file(path):
    if 'txt' in path :
        file_ = extract_text_from_txt(path)
    elif 'pdf' in path :
        file_ = extract_text_from_pdf(path)
    else :
        raise ValueError('Sorry, this function only deal with text and pdf files')

    return file_

################################################################################

import re

def clean_text(file_):
    text = re.sub('[=+,#/\?:^$@*\"※~&%ㆍ!』\\|\<\>\…》]',' ',file_)
    text = re.sub('[provider:earticle]','',file_)
    text = re.sub('www.earticle.net','',file_)
    text = text.replace("\n",'')
    return text

def find_start_page(file_,special_case=False) :
    '''
    special_case : 문서에 장 수를 나눠주는, \x0c 특수문자가 없을 때 적용하는 것입니다. 모든 참고문헌을 읽어드릴 수는 없습니다.
    '''
    if special_case :
        try :
            if len(re.findall('\(20[0-9]{2}\)|\(19[0-9]{2}\)',file_[len(file_)//2:])) > 5:
                references_page_index = \
                [m.start() for m in re.finditer('\(20[0-9]{2}\)|\(19[0-9]{2}\)',file_) if m.start() > len(file_)/2][0]

            else :
                references_page_index = \
                [m.start() for m in re.finditer('[0-9]{2,}[-][0-9]{2,}',file_) if m.start() > len(file_)/2][0]
        except : raise ValueError('there is no notation about References')
    else :
        ls = ['^references','[^a-zA-Z가-힣]references','참고 문헌','참 고 문 헌','참  고  문  헌' ,'참조문헌' ,'참고문헌','<참 고 문 헌>']#'reference''
        page_ls = [i for i in file_.split("\x0c") if i]
        catch_ls = [idx for idx,page in enumerate(page_ls[len(page_ls)//2:]) for i in ls if re.search(i,page.lower())]
        if len(catch_ls) == 0 : raise ValueError('there is no notation about References')
        catch_ls = list(set(catch_ls))

        detect_ls = []
        for i in catch_ls :
            process_ls = []
            for j in ls :
                if re.search(j,page_ls[len(page_ls)//2 + i].lower()) :
                    process_ls.append(re.search(j,page_ls[len(page_ls)//2 + i].lower()))
            detect_ls.append(process_ls)
        idx_ls = [(idx,val[0].start()) for idx,val in enumerate(detect_ls)][0]
        if idx_ls[1] > 150 :
            warnings.warn("the location of References is on the {}th in the page.".format(idx_ls[1]))

        references_page_index = len(page_ls)//2 + catch_ls[idx_ls[0]]
    return references_page_index

def find_end_page(start_page,file_) :
    except_page_ls = []
    page_ls = file_.split("\x0c")[start_page:]
    ls = ['표 1','테이블 1','테이블','테 이 블 1','테 이 블','table 1','table','appendix','appendix 1','부록','부 록',\
        '표 i','테이블 i','테 이 블 I','table i','appendix i','endnotes','figure i','figure']

    for idx,page in enumerate(page_ls) :
        for i in ls :
            if i in page.lower() :
                except_page_ls.append(idx)

    if '”' in ','.join(page_ls) :
        try :
            new_last_page = \
                np.max([idx for idx,val in enumerate(page_ls) if re.search('”',val)])
            return start_page + new_last_page + 1
        except : pass

    if len(except_page_ls) > 0 :
        return start_page + min(except_page_ls) + 1

    else :
        try :
            new_last_page = \
            np.max([idx for idx,val in enumerate(page_ls) if re.search('[0-9]+[-][0-9]+',val)])
            return start_page + new_last_page + 1
        except : return -1

def slicing_the_references(start_page,end_page,file_,special_case=False) :
    if not special_case :
        page_ls = [i for i in file_.split('\x0c') if i]
    else : page_ls = (file_ + '.')[:-1]
    if end_page == -1 :
        return page_ls[start_page : ]
    else : return page_ls[start_page : end_page]

def total_process_to_slicing_the_references(slicing_ls,special_case=False):
    if special_case :
        return slicing_ls
    else :
        ls = ['references','참고 문헌','참 고 문 헌','참  고  문  헌' , '참고문헌','참조문헌','<참 고 문 헌>','reference']
        start_idx = \
    [re.search(i,slicing_ls[0].lower()).end() for i in ls if i in slicing_ls[0].lower()][0]
        slicing_ls[0] = slicing_ls[0][start_idx :]
        return slicing_ls

def split_sentences(slicing_ls , file_,remove_duplicated=True,special_case=False):
    if not special_case :
        refer = [re.sub('[-]\s[0-9]+\s[-]','',i) for i in slicing_ls]
        refer = ','.join(refer).replace(',',' ').replace('  ',' ')
    else : refer = (slicing_ls + '.')[:-1]

    loop_ls = re.findall('Download by IP [0-9]{,3}.[0-9]{,3}.[0-9]{,3}.[0-9]{,3} at',refer)
    try :
        for _ in range(len(loop_ls)) :
            start_point = re.search('Download by IP [0-9]{,3}.[0-9]{,3}.[0-9]{,3}.[0-9]{,3} at',refer).start()
            end_point = re.search(' [0-9]{2} 2018 [0-9]{1}[:]*[0-9]{2} [A-Z]M',refer).end()
            refer = refer[:start_point] + refer[end_point:]
    except : pass

    regex_threshold = 'pp\s*\.?\s[0-9]{1,4}\s[0-9]{1,4}[.]*|\s*[0-9]{1,4}\s*[-]\s*[0-9]{1,4}[.]*|pp\s*\.?\s*[0-9]{1,4}\s*[-]\s*[0-9]{1,4}[.]*'
    refer_ls = \
    [i for i in [val for idx,val in enumerate(re.split(regex_threshold,refer))] if i]

    tuning_process1 = []

    for i in range(len(refer_ls)) :
        regex_threshold = '[20[0-9]{2}[ \d{6} ]*[.]|[19[0-9]{2}[ \d{6} ]*[.]'
        split_ls = re.split(regex_threshold,refer_ls[i])
        findall_ls = re.findall(regex_threshold,refer_ls[i])
        tuning_process1 += \
        [split_ls[idx] + findall_ls[idx] if idx != len(split_ls)-1 else split_ls[-1] for idx in range(len(split_ls))]

    tuning_process1 = [i.strip() for i in tuning_process1]

    tuning_process2 = []

    for i in range(len(tuning_process1)) :
        regex_threshold = '[(].{0,5}\s*20[0-9]{2}.{0,5}\s*[)][.]|[(].{0,5}\s*19[0-9]{2}.{0,5}\s*[)][.]'
        split_ls = re.split(regex_threshold,tuning_process1[i])
        findall_ls = re.findall(regex_threshold,tuning_process1[i])
#        split_ls = re.split('[(]20[0-9]{2}[a-zA-Z]*[)][.]|[(]19[0-9]{2}[a-zA-Z]*[)][.]',tuning_process1[i])
#        findall_ls = re.findall('[(]20[0-9]{2}[a-zA-Z]*[)][.]|[(]19[0-9]{2}[a-zA-Z]*[)][.]',tuning_process1[i])
        tuning_process2 += \
        [split_ls[idx] + findall_ls[idx] if idx != len(split_ls)-1 else split_ls[-1] for idx in range(len(split_ls))]

    tuning_process2 = [i.strip() for i in tuning_process2 if i]

    if remove_duplicated :
        in_korean_ls , translated_eng_ls =[],[]
        if '(in korean)' in refer.lower() :
            in_korean_ls = [tuning_process2[idx-1] for idx,val in enumerate(tuning_process2) if '(in korean)' in val.lower()]
        if '(translated in english)' in refer.lower() :
            translated_eng_ls = \
            [tuning_process2[idx] for idx,val in enumerate(tuning_process2) if '(translated in english)' in val.lower()]

        exception_ls = in_korean_ls + translated_eng_ls
        for idx in range(len(exception_ls)) :
            tuning_process2.remove(exception_ls[idx])

    tuned_refer_ls = [i.replace('(in Korean).','').replace('(In Korean).','').strip() for i in tuning_process2]


    return tuned_refer_ls
