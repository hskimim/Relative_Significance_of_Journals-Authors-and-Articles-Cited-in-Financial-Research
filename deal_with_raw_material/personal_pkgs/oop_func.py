import oop_function as ref

class Slicing_paper:

    def __init__(self, pdf_path,special_case):
        self.pdf_path = pdf_path
        self.special_case = special_case
        self.file_ = ref.extract_text_from_file(self.pdf_path)
        self.clean_text = ref.clean_text(self.file_)
        self.start_page = ref.find_start_page(self.clean_text,self.special_case)
        self.end_page = ref.find_end_page(self.start_page , self.clean_text)
        self.slice = ref.slicing_the_references(self.start_page , self.end_page , self.clean_text,self.special_case)
        self.fine_slice = ref.total_process_to_slicing_the_references(self.slice,self.special_case)

    def split(self):
        self.split = ref.split_sentences(self.fine_slice,self.clean_text,special_case=self.special_case)
        return self.split
