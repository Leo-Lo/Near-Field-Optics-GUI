from bokeh.io import *
from bokeh.layouts import *
from bokeh.plotting import *
from bokeh.models.renderers import *
from bokeh.palettes import *
from bokeh.models.widgets import *
from bokeh.models import *
from bokeh import events

from NearFieldOptics import Materials as M
from NearFieldOptics import TipModels as T
from numpy import *
import matplotlib.pyplot
from matplotlib import pyplot as plt

output_notebook()
#output_file("new GUI layout.html")


def modify_doc(doc):
    
    #FIRST LAYER        
    def title():
        text = Div(text="<h1><b>The Lightning Rod Model GUI</b></h1>",width=400, height=30)
        title = WidgetBox(text, width=400)
        return [title]
    def CUlogo():
        callback1 = CustomJS(code="alert('Don't drag away the logo!')")
        tap = TapTool(callback=callback1)
        cu = figure(x_range=(0,6), y_range=(-3.5,0.2),width=330,height=60,toolbar_location=None, tools=[tap])
        cu.image_url(url=['Columbia logo.png'], x=0, y=0.2,w=6, h=3.5)
        cu.xgrid.grid_line_color = None
        cu.ygrid.grid_line_color = None
        cu.axis.visible = False
        return [cu]
    def BasovLogo():
        callback1 = CustomJS(code="alert('Don't drag away the logo!')")
        tap = TapTool(callback=callback1)
        basov = figure(x_range=(0,6), y_range=(-3.5,0.2),width=200,height=60,toolbar_location=None, tools=[tap])
        basov.image_url(url=['basov lab logo.png'], x=0, y=0.2,w=6, h=3.5)
        basov.xgrid.grid_line_color = None
        basov.ygrid.grid_line_color = None
        basov.axis.visible = False
        return [basov]
    def space():
        empty = Div(text="",width=400, height=1)
        space = WidgetBox(empty, width=400)
        return [empty]

    #widgets
    matDim = RadioButtonGroup(labels=["2D", "3D"], active=0)
    subMat = Select(title="Substrate material:", value="Si_80K", options=["Si_80K", "Si_150K", "Si_300K", "SiO2"])
    thickness = TextInput(title="Thickness (nm): ",value="0")
    add = Button(label="Add a layer on top", button_type="primary")
    
    size = TextInput(title="Tip apex radius size (nm): ",value="10")
    oscAmplitude = TextInput(title="Tip oscillation amplitude (nm): ",value="80")
    
    freqNum = TextInput(title="# of frequency points: ",value="256")
    numQ = TextInput(title="# of q points: ",value="244")
    numZ = TextInput(title="# of z points: ",value="40")
    
    normFreq = TextInput(title="Normalization frequency (cm^-1): ",value="0")
    normMat = Select(title="Normalization material:", value="Au", options=["Au","Si_80K", "Si_150K", "Si_300K", "SiO2"])
        
    panel = Select(title="Plot panel",value="Plot in 1st panel", options=["Plot in 1st panel", 
        "Plot in 2nd panel", "Plot in 3rd panel", "Plot in 4th panel"])
    
    quantity = Select(title="Quantity to calculate:", value="permittivity", options=[ 
            "far-field reflectivity (p-polarized)", "far-field reflectivity (s-polarized)","far-field transmission",
            "near-field reflectivity","near-field signal","permittivity"])

    #graphs
    s1 = figure(x_axis_label='frequency',plot_width=500, plot_height=300)
    s1.xgrid.grid_line_color = None
    s1.ygrid.grid_line_color = None
        
    s2 = figure(x_axis_label='frequency',plot_width=500, plot_height=300)
    s2.xgrid.grid_line_color = None
    s2.ygrid.grid_line_color = None

    s3 = figure(x_axis_label='frequency',plot_width=500, plot_height=300)
    s3.xgrid.grid_line_color = None
    s3.ygrid.grid_line_color = None
        
    s4 = figure(x_axis_label='frequency',plot_width=500, plot_height=300)
    s4.xgrid.grid_line_color = None
    s4.ygrid.grid_line_color = None
        
    run = Button(label="Run!", button_type="success")
    clear = Button(label="Clear graph",button_type="warning")
    
    #interact
    
    def update_parameters():
        
        sample=M.TabulatedMaterialFromFile(subMat.value+'.csv')
        thick=float(thickness.value)*1e-9
        a=float(size.value)*1e-9
        amplitude=float(oscAmplitude.value)*1e-9
        freqNumber=int(freqNum.value)
        Nqs=int(numQ.value)
        Nzs=int(numZ.value)
        normFrequency=float(normFreq.value)
        normMaterial=normMat.value
        
        f0=sample._eps_data.axes[0]
        freqs=linspace(f0.min(),f0.max(),freqNumber)
        
        ##only plot at 1st panel; generalize to allow radio button group determine which panel to plot

        if panel.value=="Plot in 1st panel":
            graph=s1
        elif panel.value=="Plot in 2nd panel":
            graph=s2
        elif panel.value=="Plot in 3rd panel":
            graph=s3
        elif panel.value=="Plot in 4th panel":
            graph=s4
        else:
            graph=s1

            
        if quantity.value=="near-field signal":
            ##no normalization
            calculated=T.LightningRodModel(freqs,rp=sample.reflection_p,a=a,Nqs=Nqs,Nzs=Nzs,\
                                            amplitude=amplitude,normalize_to=None,\
                                            normalize_at=normFrequency)
            global nfs
            nfs=graph.line(freqs,abs(calculated['signal_3']),legend="s3",line_color="#0093dd",line_width=2)
            graph.title.text=subMat.value
            graph.title.align="center"

        elif quantity.value=="far-field reflectivity (p-polarized)":
            ##picked angle 0 as default, generalize
            rp_farfield=sample.reflection_p(freqs,angle=0)
            global fReflecP
            fReflecP=graph.line(freqs,abs(rp_farfield),legend="far field (p) amplitude",line_color="#0093dd",line_width=2)
            graph.title.text=subMat.value
            graph.title.align="center"

        elif quantity.value=="far-field reflectivity (s-polarized)":
            ##picked angle 0 as default, generalize
            rs_farfield=sample.reflection_s(freqs,angle=0)
            global fReflecS
            fReflecS=graph.line(freqs,abs(rs_farfield),legend="far field (s) amplitude",line_color="#0093dd",line_width=2)
            graph.title.text=subMat.value
            graph.title.align="center"

        #need to add far-field transmission

        elif quantity.value=="permittivity":
            eps=sample.epsilon(freqs)
            global rl
            rl=graph.line(freqs,eps.real,legend="real",line_color="#0093dd",line_width=2)
            global img
            img=graph.line(freqs,eps.imag,legend="imaginary",line_color="orange",line_width=2)
            graph.title.text=subMat.value
            graph.title.align="center"

        elif quantity.value=="near-field reflectivity":
            rp_nearfield=sample.reflection_p(freqs,angle=None,q=1/a)
            global nReflec
            nReflec=graph.line(freqs,abs(rp_nearfield),legend="near field amplitude",line_color="orange",line_width=2)
            graph.title.text=subMat.value
            graph.title.align="center"

        else:
            #plot a thick red cross on panel
            x1 = linspace(0, 10, 100)
            y1 = x1
            y2 = 10-x1
            global x
            x=graph.line(x1, y1, legend="ERROR", line_color="red", line_width=6)
            global xx
            xx=graph.line(x1, y2, legend="ERROR", line_color="red", line_width=6)
            graph.title.text=subMat.value
            graph.title.align="center"

    
    def clear_graph():
        if panel.value=="Plot in 1st panel":
            graph=s1
        elif panel.value=="Plot in 2nd panel":
            graph=s2
        elif panel.value=="Plot in 3rd panel":
            graph=s3
        elif panel.value=="Plot in 4th panel":
            graph=s4
        else:
            graph=s1
           
        if quantity.value=="near-field signal":
            graph.renderers.remove(nfs)
        elif quantity.value=="far-field reflectivity (p-polarized)":
            graph.renderers.remove(fReflecP)
        elif quantity.value=="far-field reflectivity (s-polarized)":
            graph.renderers.remove(fReflecS)
        elif quantity.value=="permittivity":
            graph.renderers.remove(rl)
            graph.renderers.remove(img)
        elif quantity.value=="near-field reflectivity":
            graph.renderers.remove(nReflec)
        else:
            graph.renderers.remove(x)
            graph.renderers.remove(xx)
            
    
    run.on_click(update_parameters)
    clear.on_click(clear_graph)


    #layout
    l = layout([title(),CUlogo(),BasovLogo()],
        [space()],[WidgetBox(matDim,subMat,thickness,add, width=200),[s1,s3],[s2,s4]],
        [WidgetBox(size,oscAmplitude,width=250),WidgetBox(freqNum,numQ,numZ,width=250),WidgetBox(normFreq,normMat,width=250),WidgetBox(panel,width=250),WidgetBox(quantity,run,clear,width=250)])

    doc.add_root(l)

# put the results in a row
show(modify_doc)