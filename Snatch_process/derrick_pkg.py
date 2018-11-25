import io
import re
import pandas as pd
import numpy as np
from IPython.display import display , Markdown

from pdfminer.converter import TextConverter
from pdfminer.pdfinterp import PDFPageInterpreter
from pdfminer.pdfinterp import PDFResourceManager
from pdfminer.pdfpage import PDFPage

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

# read text file
def extract_text_from_txt(text_path):
    with open(text_path,'rt') as f :
        lines = f.readlines()
    # return ','.join(lines).replace('\n','')
    return ','.join(lines)

def extract_file_content(file_path) : 
    if 'pdf' in file_path : 
        file_ = extract_text_from_pdf(file_path)
    
    else : 
        file_ = extract_text_from_txt(file_path)
        
        
    return file_



################################################################################

#def find_start_idx(file_) :
    """
    참고 문헌의 시작점을 찾아주는 함수입니다.
    file_ : file path
    """
#    ls = ['References','REFERENCES','reference','Reference','REFERENCE','참고 문헌','참 고 문 헌','참  고  문  헌' , '참고문헌','<참 고 문 헌>','Reference','reference','REFERENCE']
 #   start_idx = []
 #   start_idx = [re.search(str(i),file_) for i in ls]
 #   start_idx = [i.end() for i in start_idx if (i) and (i.start() > len(file_)//2)]
    
 #   if (start_idx != []) and (start_idx[0] < len(file_)) : return start_idx[0]
    
 #   else : #만약 ls 로 정해놓은 패턴의 글자가 논문 내에 없다면
  #      start_idx = [re.search(str(i),file_).end() for i in ls if re.search(i,file_)]
  #      if (start_idx != []) and (start_idx < len(file_)) : return start_idx[0]
 #       else :
  #          raise ValueError
            
def find_start_idx(file_) :
    """
    참고 문헌의 시작점을 찾아주는 함수입니다.
    file_ : file path
    """
    ls = ['References','REFERENCES','reference','Reference','REFERENCE','참고 문헌','참 고 문 헌','참  고  문  헌' , '참고문헌','<참 고 문 헌>','Reference','reference','REFERENCE']
    start_idx = [[m.start(0) for m in re.finditer(i,file_)] for i in ls]
    start_idx = [k for j in [i for i in start_idx if i] for k in j if k > len(file_) // 2]
    
    if start_idx != [] : return np.max(start_idx)
    
    else : raise ValueError #만약 ls 로 정해놓은 패턴의 글자가 논문 내에 없다면 ValueError 반환
        
def find_end_idx(file_):
    """
    논문 내에서 참고 문헌이 끝나는 지점을 알려주는 함수입니다.
    file_ : file path
    """
    references = file_[find_start_idx(file_):] # references 는 find_start_idx에서 정해준 시작점부터 시작합니다.
    ls = ['표 1','테이블 1','테이블','테 이 블 1','테 이 블','table 1','Table','Table 1','TABLE 1','TABLE' ,'Appendix','Appendix 1','appendix 1','APPENDIX 1','부록','부 록','Endnotes','Figure 1','FIGURE 1',\
    '표 I','테이블 I','테 이 블 I','table I','Table I','TABLE I' ,'Appendix I','appendix I','APPENDIX I','부록','부 록','Endnotes','Figure I','Figure','FIGURE I'] # 논문에서 표나 테이블 부록이 있는 경우, 참고문헌의 끝이 논문의 끝이 아니게 됩니다.
    testing_ls = [re.search('[\S]*'+str(i)+'[\S]*',references) for i in ls] # 논문 내에서 ls라는 패턴이 있는 경우의 인덱스를 잡아냅니다.
    testing_val = [idx for idx,val in enumerate(testing_ls) if val != None] # 논문 내에서 ls라는 패턴이 있는 경우의 인덱스를 잡아냅니다.
    testing_idx = [val.start() for idx,val in enumerate(testing_ls) if val != None] # 패턴의 인덱스 중 시작점만 잡아냅니다.
    
    if testing_idx != []: # 패턴을 발견한 경우 해당 패턴의 시작점이 참고 문헌의 끝점이 됩니다.
        return find_start_idx(file_) +  int(np.min(testing_idx))

    else : # 없는 경우, 논문 내에서 마지막 페이지 수가(000-000 패턴) 발견되는 지점이 마지막 참고문헌의 포인트가 됩니다.
        #end_idx = [(m.start(0),m.end(0)) for m in re.finditer(re.findall('[0-9]+[-][0-9]+',file_)[-1],file_)][-1][1]
        end_idx = len(file_)
        if end_idx < find_start_idx(file_) : # 마지막 지점이 시작점보다 앞의 지점이면 문제가 있는 것으로 간주하고 에러문을 반환합니다.
            raise ValueError
        else : 
            return end_idx
        
def make_references(file_): 
    """
    find_start_idx , find_end_idx 함수의 번들 함수입니다.
    file_ : string type으로 만든 content 를 넣어주어야 합니다.
    """
    start_idx = find_start_idx(file_)
    end_idx = find_end_idx(file_)
    
    content_ = file_[start_idx:end_idx]
    page_ls = content_.split('\x0c')    
    tuning_ls1 = [val for idx,val in enumerate(page_ls) if '�' not in val] # �가 들어있는 경우 표일 가능성이 높습니다.
        
    return ','.join(tuning_ls1).replace(',','')
    

#########################################################################3

def find_page_idx(file_):
    page_ls = []
    page_idx = [re.search((re.findall('\x0c[\d]*',file_)[i]),file_).end() for i in range(len(re.findall('\x0c[\d]+',file_)))]
    for idx,val in enumerate(page_idx):
        if idx ==0 :
            page_ls.append(file_[:val])
        else : page_ls.append(file_[page_idx[idx-1]:page_idx[idx]])
    return page_ls

def find_start_page(file_):
    ls = ['references','References','REFERENCES','참고 문헌','참 고 문 헌','참  고  문  헌' , '참고문헌','<참 고 문 헌>','Reference','reference','REFERENCE']
    ref_page = [idx for idx,val in enumerate(find_page_idx(file_)) for i in ls if i in val]
    if ref_page != [] : return ref_page[0]
    else :
        display(Markdown('### you should find another constraint'))
        print(file_)

def find_end_page_ex(file_):
    page_file = ref1.find_page_idx(file_)
    start_page = ref1.find_start_page(file_)
    ls3 = ['“' , '”' , '19[0-9]{2}' , '20[0-9]{2}' , 'Journal' , '[0-9]+[-][0-9]+']
    if len(page_file[start_page:]) == 1 : return 1
    for idx,page in enumerate(reversed(page_file[start_page:])):
        if (len(page_file[start_page:])-idx-1) > start_page :
            for i in ls3 :
                if len(re.findall(i,page)) <2 : pass
                else : return  len(page_file[start_page:])-idx-1
        else : return -1

def make_references_page(file_):
    page_file = find_page_idx(file_)
    start_page = find_start_page(file_)
    end_page = find_end_page(file_)
    return page_file[start_page:start_page+end_page]

################################################################################

def get_jaccard_sim(str1, str2): 
    a = set(str1.split()) 
    b = set(str2.split())
    c = a.intersection(b)
    return float(len(c)) / (len(a) + len(b) - len(c))























