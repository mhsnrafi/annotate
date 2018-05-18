import pandas as pd
import numpy as np
from traitlets import Int, Instance, Unicode, link
from ipywidgets import Button, VBox, HBox, HTML, Box, Layout, Label, \
                        Text, Textarea, ToggleButtons, HTML, Checkbox, IntSlider, \
                        SelectMultiple

class RegexUI(VBox):
    _current_position = Int(0, allow_none = False).tag(sync = True)
    _state = Unicode('', allow_none = False).tag(sync = True)

    def __init__(self, 
        rgx_mchr,
        *args, **kwargs):

        super(VBox, self).__init__(*args, **kwargs)

        self._rgx_mchr=rgx_mchr
        self._state=self._init_state()
        self._draw()
        link((self,'_current_position'),(self._rgx_mchr, 'sno'))
        self.observe(self._draw, names=['_state', '_current_position'])   

        

    def _init_state(self,):
        self._states=self._rgx_mchr.get_states()+["Prod Dict",]
        return self._states[-1]

    def _draw(self, change = None):

        form_layout = Layout(display='flex', justify_content='center',align_items='center', width='100%', )
        
        controls = VBox(layout = form_layout)
        controls.children += (ToggleButtons(options=(self._states), 
                                                value=self._state,                                               
                                                description='Regex Type:',
                                                disabled=False,),)

        link ((self,'_state'), (controls.children[0],'value'))

        if self._state=="Prod Dict":
            #self._rgx_mchr.sno=self._current_position
            self._rgx_mchr.update_prd_rgx()
            controls.children +=(self.make_dict_ctrl(),)


        controls.children += (Text(value = self._rgx_mchr.get_regex(self._state), description="Regex Text",
                                    layout = Layout(width = '70%',height='100px', )),)
        
        controls.children += (HTML(self._rgx_mchr.get_annotated_docs(self._state),layout = Layout(width = '100%', border='solid 2px')),)

        
        
        self.children = (controls,)


    def make_dict_ctrl(self):
        form_layout = Layout(display='flex', justify_content='center', width='100%', height='350px')

        ctrl_box_lo=Layout(display='flex', justify_content='center')
        controls = HBox([ Button(description='Prev'), 
                                    Button(description='Next'), 
                                    Text(value = str(self._current_position), layout = Layout(width = '80px')),
                                    Label(value = 'out of', layout = Layout(width = '35px')),
                                    Text(value = str(self._rgx_mchr.get_pdct_size()), disabled = True)], layout = ctrl_box_lo)
        
        affix_box= HBox([ self._make_affix_box(a_e) for a_e in [('pre','pe','pdt','popt'), ('inf','ie','idt','iopt'), ('suf','se','sdt','sopt')]], 
                        layout = ctrl_box_lo)
                                         
        controls.children[0].on_click(self._click_prev)
        controls.children[1].on_click(self._click_next)
        controls.children[2].observe(self._int_text_value_changed, names='value')

        controls2= HBox([ Button(description='Apply'), Button(description='Update'), ], layout = ctrl_box_lo)
        controls2.children[0].on_click(self._apply)
        controls2.children[1].on_click(self._update)


        return VBox([controls,affix_box, controls2], layout=form_layout)
    
    def _make_affix_box(self, a_e):
        aff=getattr(self._rgx_mchr, a_e[0])
        err=getattr(self._rgx_mchr, a_e[1])
        dct=getattr(self._rgx_mchr, a_e[2])
        opt=getattr(self._rgx_mchr, a_e[3])

        form_item_layout = Layout(display='flex', flex_flow='column', align_items='stretch', display_content='center')
        ctrl = VBox([Checkbox(value=opt,description=a_e[0]+'fix',),
                    Text(value=aff,),
                    IntSlider(value=err,min=0, max=6, readout=True,),
                    SelectMultiple(options=dct),
                    ], layout=form_item_layout)
        #ctrl.children[1].disabled = not ctrl.children[0].value
        link((self._rgx_mchr,a_e[0]),(ctrl.children[1],'value'))
        link((self._rgx_mchr,a_e[1]),(ctrl.children[2],'value'))
        link((self._rgx_mchr,a_e[3]),(ctrl.children[0],'value'))
        return ctrl
        

    def _click_prev(self,button):
        self._current_position = max(self._current_position - 1, 0)
        
    def _click_next(self,button):
        self._current_position = min(self._current_position + 1, self._rgx_mchr.get_pdct_size())

    def _apply(self,button):
        self._rgx_mchr.update_prd_rgx()
        self._draw()
    
    def _update(self,button):
        pass
    
    def _int_text_value_changed(self, change):
        try:
            new_value = int(change['new'])
        except ValueError:
            return
        
        if new_value < 0:
            new_value = self._rgx_mchr.get_pdct_size() + new_value
            if new_value < 0:
                return
        
        if new_value >= self._rgx_mchr.get_pdct_size():
            return
            
        self._current_position = new_value


