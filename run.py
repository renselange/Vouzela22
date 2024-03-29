import streamlit as st
import typing_extensions
import pandas as pd
import numpy as np
import datetime as dt
from os.path import getmtime
import plotly.express as px  # interactive charts
import matplotlib as plt

from read_data import read_vouzela_excel #, collect_enchantment_responses, enchantment_order
from word_cloud import make_image
from enchantment_pre_process import item_to_seq, seq_to_item

st.set_page_config(
    page_title="Vouzela Tourism Dashboard",
    page_icon="✅",
    layout="wide"
)


uploadFile = 'POCPWA_AppExport_15-3-2022.xlsx'


if uploadFile:

    dd,born = read_vouzela_excel(uploadFile) # ,dt.datetime(1922,3,3),dt.datetime(3022,3,3)) 

    st.session_state.first_day = min(dd['dateEnd'])
    st.session_state.last_day = max(dd['dateEnd'])

    st.session_state.first_day = st.sidebar.date_input('yAjuste la fecha de inicio según sea necesario:', st.session_state.first_day,key='what 1')
    st.session_state.last_day  = st.sidebar.date_input('yAjuste la fecha de cierre según sea necesario:', st.session_state.last_day,key='what 2')
    st.sidebar.write('Reinicie el programa para restablecer el rango de fechas')

    if st.session_state.last_day < st.session_state.first_day : st.session_state.last_day = st.session_state.first_day

    temp = dd[(dd['dateEnd'].dt.date >= st.session_state.first_day) & (dd['dateEnd'].dt.date <= st.session_state.last_day)]
    
    if temp.shape[0] == 0:
        '# request not executed'
    else:
        dd = temp

    st.write('Carregado de "%s"'%uploadFile,'com',dd.shape[0],'casos completos. %s %s'%(st.session_state.first_day,st.session_state.last_day)) 
    
    when = '''Dados Vouzela até %s'''%born


page = st.sidebar.radio(
    when, [
    "1. Vista rápida ...",
    "2. Inspecione o arquivo de dados", 
    "3. Contagens de frequência simples", 
    "4. Wordclouds de respostas escritas",
    "5. Encantamento específico do país"], index=0
)


if page.startswith('1.'):

    st.write('Recuento semanal de encuestados por nacionalidad (planned: the Sunday date of the week as label)')
    dates = [int(w) for w in dd['dateEnd'].dt.isocalendar().week.tolist()]
    visitors = pd.DataFrame({'week':dates, 'Nacionalidade': dd['Nacionalidade']})
    xt = pd.crosstab(visitors['week'],visitors['Nacionalidade'])
    xt.columns = ['%s:O'%v for v in xt.columns] 
    st.bar_chart(xt)

    '# To be added:'
    '- Number of enchantedness items checked by week x nationality'
    '- Satisfaction by week x nationality'
    '- Any other ideas ? Intention: show the most useful stuff immediately'
    'LATER: Click on map of Vouzela (e.g., a resto) and get info'

##################### show entire data table ##################

if page.startswith('2.'):

    st.write('Casos classificados mais recentes primeiro')
    st.dataframe(dd)

##################### show frequency + figute + stats (if possible) ########

elif page.startswith('3.'):

    for seq,v in enumerate(list(dd.columns)): 
        '# Questão: %s [%d]'%(v,seq)
        '[Clique no cabeçalho da coluna para classificar]'
        st.write(dd[v].value_counts())
        try:
            st.bar_chart(dd[v].value_counts())
            st.write(dd[v].describe()) # this will crash if vals are non-numeric
        except:
            pass

##################### show word clouds for open-ended questions ###########

elif page.startswith('4.'):

    for f in dd.columns[28:33]:
        '**%s**'%f
        text = ' '.join(list(dd[f].astype(str)))
        st.image(make_image(text))
        'Por favor, também inspecione as listas de respostas abaixo:'
        st.write(dd[f].value_counts())

##################### show % of enhcantment items being endorsed #########

elif page.startswith('5.'):

    #### to include the other languages, translate to Portuguese first
    #### "prefix" the translation by country: PT-Encantando, EN-Encantando

    '# Os padrões de encantamento variam de acordo com o país de origem?'

    dd['temp_country'] = dd.apply(lambda cols: 'pt' if cols['Sexo'].startswith('F') else 'en',axis=1) # remove later ....

    item_list = [seq_to_item[seq] for seq in range(16)] + ['COL-TOTAL']

    enchanted = pd.DataFrame({'Fonte de Encantamento': item_list})

    for country in dd['temp_country'].unique():

        this_country = dd[dd['temp_country'] == country]

        as_list      = ((this_country[dd.columns[20]] + '\n').astype(str).values.sum()[:-1]).split('\n')   # all items in one long list
        new_freq     = [0]*17 # one more for the TOTAL
        for w in as_list: new_freq[item_to_seq[w][0]] += 1
        new_freq[-1] = sum(new_freq)
        enchanted[country.upper()+'-count'] = new_freq

    enchanted['ROW-TOTAL'] = enchanted.apply(lambda cols: sum(cols[v] for v in enchanted.columns if not v.startswith('Fonte')),axis=1)
    enchanted.sort_values(by='ROW-TOTAL',inplace=True)

    
    st.write(enchanted)


    bar_fig = plt.pyplot.figure(figsize=(3,1.5),tight_layout=True)
    bar_ax = bar_fig.add_subplot(111)

    sub_enchanted = enchanted.iloc[:-1,1:-1] 
    sub_enchanted.index = enchanted['Fonte de Encantamento'].iloc[:-1]
    sub_enchanted.plot.bar(alpha=0.5, ax=bar_ax) #, title="counts *** simulated data here")

    st.pyplot(bar_fig)









