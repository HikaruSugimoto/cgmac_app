import streamlit as st
import pandas as pd
import statsmodels.api as sm
from PIL import Image
import zipfile
import os
st.set_page_config(layout="wide")
st.title('CGMac app')
st.write('This app calculates measures derived from continuous glucose monitoring (CGM) of multiple individuals. It processes time series glucose data and calculates various statistical measures including mean glucose levels (Mean), standard deviation (Std) and temporal autocorrelation properties (AC_Mean and AC_Var).')
st.write('This app accepts CGM data in the following format. Missing values should be interpolated. In addition, data from the first day may be less reliable. Furthermore, the number of measurement days can affect AC_Mean and AC_Var, so it may be necessary to standardise the measurement period across participants.')
image=Image.open("CGM_data.png")
st.image(image,width=600)


if(os.path.isfile('demo.zip')):
    os.remove('demo.zip')
with zipfile.ZipFile('demo.zip', 'x') as csv_zip:
    csv_zip.writestr("CGM_data.csv", 
                    pd.read_csv("CGM_data.csv").to_csv(index=False))        
with open("demo.zip", "rb") as file: 
    st.download_button(label = "Download demo data",data = file,file_name = "demo.zip")

st.write('Autocorrelation functions depend on the lag, which determines how many time points to shift. While we have shown that lag 30 appears to work well for CGM data taken at 5-minute intervals (Sugimoto, Hikaru, et al. "Improved Detection of Decreased Glucose Handling Capacities via Novel Continuous Glucose Monitoring-Derived Indices: AC_Mean and AC_Var." medRxiv (2023): 2023-09. Sugimoto, Hikaru, et al. "Three components of glucose dynamics-value, variability, and autocorrelation-are independently associated with coronary plaque vulnerability." medRxiv (2023): 2023-11.), the optimal lag is unknown when the time interval is different.')

#Input
st.subheader('Upload CGM data')
df = st.file_uploader("", type="csv")

lagt=st.slider('Lag (used for AC_Mean and AC_Var calculation):', min_value=1, max_value=60, value=30, step=1)

if df is not None:
    df =pd.read_csv(df)
    AC= pd.DataFrame()
    for i in range (0,len(df.iloc[:,0])):
        X = df.iloc[i,1:]
        dff=pd.DataFrame(sm.tsa.stattools.acf(X,nlags=lagt,fft=False))
        AC=pd.concat([AC, pd.DataFrame([df.iloc[i,0],X.mean(),X.std(),dff.iloc[1:].mean()[0],dff.iloc[1:].var()[0]]).T])
    AC=AC.rename(columns={0: 'ID'}).rename(columns={1: 'Mean'}).rename(columns={2: 'Std'}).rename(columns={3: 'AC_Mean'}).rename(columns={4: 'AC_Var'})
    st.write(AC.set_index('ID'))

    if(os.path.isfile('CGM_AC.zip')):
        os.remove('CGM_AC.zip')
    with zipfile.ZipFile('CGM_AC.zip', 'x') as csv_zip:
        csv_zip.writestr("CGM_AC.csv",
                        AC.to_csv(index=False))
    with open("CGM_AC.zip", "rb") as file: 
        st.download_button(label = "Download the result",
                        data = file,file_name = "CGM_AC.zip")

st.subheader('License')
st.write('This web app is licensed free of charge for academic use and we shall not be liable for any direct, indirect, incidental, or consequential damages resulting from the use of this web app. In addition, we are under no obligation to provide maintenance, support, updates, enhancements, or modifications.')
