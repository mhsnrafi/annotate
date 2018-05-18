import numpy as np
import pandas as pd
import re
import regex
from spacy import displacy
from traitlets import Int, Instance, Unicode, Set, Bool, link, HasTraits


class Regex_Matcher(HasTraits):
    sno,pe,ie,se = Int(0), Int(0), Int(0), Int(0)
    pre,inf,suf = Unicode(''), Unicode(''), Unicode('')
    pdt,idt,sdt = Set(), Set(), Set()
    popt, iopt, sopt = Bool(True), Bool(True), Bool(True)


    def __init__(self, 
        regex_filename,
        ds_filename,
        prod_filename
        ):

        self._regex_df=pd.read_excel(regex_filename)
        self._docs_df=pd.read_csv(ds_filename)
        self._pdct_df=pd.read_excel(prod_filename, sheet_name=0, dtype=str)
        self._pdct_df=self._pdct_df.replace('nan', '', regex=True)
        #for k in ['sno','pe','ie','se',]: setattr(self, k, Int(0, allow_none = False).tag(sync = True)) 
        #for k in ['pre','inf','suf']: setattr(self, k, Unicode('', allow_none = False).tag(sync = True))

        self.sno=0
        self._docs = []    
        self._init_ds()    
        self.set_prod_dct()
        self._init_rgx_dict()        
        self.observe(self.set_prod_dct, names='sno')
        self.observe(self._set_opts, names=['popt', 'iopt', 'sopt']) 
        
        super().__init__()

    def _init_rgx_dict(self,):
        df=self._regex_df
        self._rgx_dict=dict(zip(df.Name,df.Regex))
        self._states=list(self._rgx_dict.keys())

    def _init_ds(self):
        scen_df=self._docs_df
        txt_all=scen_df.Roman.str.cat()
        self._all_docs=scen_df.English.append(scen_df.Roman)
        self._all_docs=self._all_docs.str.replace('\n',' ')

    def _set_opts(self, change=None):
        self._popt='' if self.popt else "?"
        self._iopt='' if self.iopt else "?"
        self._sopt='' if self.sopt else "?"
            
    
    def get_states(self,):
        return self._states

    def get_regex(self,state):
        if state=="Prod Dict":
            return self._rgx
        return self._rgx_dict[state]

    def get_annotated_docs(self, state):
        if state!="Prod Dict":
            self._dct_mode=False
            self._rgx = self._rgx_dict[state]
            self._apply_rgx(self._rgx)
        return displacy.render(self._docs, style='ent', manual=True,)

    def init_doc(self, s):
        return {'text':s, 'ents':[], 'title':None, }
    
    def _apply_rgx(self,rgx):
        regx=regex.compile(rgx,regex.I)
        self._docs=[];self.pdt.clear(),self.idt.clear(),self.sdt.clear()
        for i in self._all_docs:
            doc = self.init_doc(i)
            match = regx.finditer(i)
            for m in match:
                tmp=[{'start': m.start(), 'end': m.end(), 'label': 'ENT'}]
                if self._dct_mode:
                    self.pdt.add(m.groups()[0])
                    self.idt.add(m.groups()[1])
                    self.sdt.add(m.groups()[2])
                doc['ents']+=tmp
            if doc['ents']!=[]:
                self._docs.append(doc)
    
    def get_pdct_size(self):
        return len(self._pdct_df)

    def set_prod_dct(self, change=None):
        pre,inf,suf=self._pdct_df.loc[self.sno]
        pe=int(len(pre)/3); ie=int(len(inf)/3); se=int(len(suf)/3)
        self._set_params(pe,ie,se,pre,inf,suf)
        self._set_opts()
        self.update_prd_rgx()
        
    
    def _set_params(self, *args):
        for i,p in enumerate(['pe','ie','se','pre','inf','suf']):
            setattr(self, p, args[i])
    
    def update_prd_rgx(self):

        self._rgx=r'(?e:)(?:(%s){e<=%d})%s (%s){e<=%d} (?:(%s){e<=%d})%s'%(self.pre, self.pe, self._popt,
                                                                        self.inf,  self.ie,
                                                                        self.suf, self.se, self._sopt)
        self._dct_mode=True                                                    
        self._apply_rgx(self._rgx)
        
        
