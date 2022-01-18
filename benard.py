try:
  import streamlit as st
  from PIL import Image
  image = Image.open('Duplicate Names.png')
  st.sidebar.image(image,use_column_width=True)
  st.sidebar.write("""# Fuzzy Dedupe App
  ***By: Smallpdf Kenya*** """)
  link1 = '[Fuzzy Dedupe](https://fuzzydedupewebsite.unicornplatform.page/)'
  st.sidebar.markdown(link1, unsafe_allow_html=True)


  import pandas as pd
  import numpy as np
  from string_grouper import match_strings, match_most_similar, \
    group_similar_strings, compute_pairwise_similarities, \
    StringGrouper
  import warnings
  warnings.filterwarnings('ignore')
  st.write("""# Detect duplicates in spreadsheet using world-class fuzzy matching algorithms""")
  st.write("""***Just drag and drop your file.***""")
  uploaded_file = st.file_uploader("Choose a file", type=['csv', 'xlsx'])

  if uploaded_file is not None:
      try:
        data_frame = pd.read_csv(uploaded_file)
      except Exception as e:
        data_frame = pd.read_excel(uploaded_file)

      data_frame = data_frame.applymap(str)
      # store head as list (we can use as a drop down on streamlit)
      header = list(data_frame.columns)
          #Keep a clean version of the dataframe to be used later
      joindataframe = data_frame

      duplicate = st.selectbox('Column to check duplicate', data_frame.columns,index=2)
      distinct = st.selectbox('Column to check distinct', data_frame.columns,index=1)

      #Pick parameters from what customer selects as well as thresholds
      #Create on streamlit a way customer inputs colum to perform duplicate identification and column to be distinct
      # columntocheckduplicate =header[2]
      # columntobedistinct =header[1]

      columntocheckduplicate = duplicate
      columntobedistinct = distinct

      s1 = st.slider("Minimum Similarity (%)", min_value=0, max_value=100,value=85,step=5)

      if(st.button('Run')):
        data_frame = match_strings(data_frame[columntocheckduplicate],master_id = data_frame[columntobedistinct],ignore_index=True, min_similarity = s1/100)

        #Use the customer name selected + left_ and customer no + right_ (you have to define)
        leftfield='left_'+ columntocheckduplicate
        rightfield='right_'+columntocheckduplicate
        data_frame = data_frame[data_frame[leftfield] != data_frame[rightfield]]

        data_frame = data_frame.reset_index(drop=True)
        data_frame = data_frame.rename(columns={"index":"0rank"})
        data_frame['0rank'] = data_frame.index + 1

        data_frame1 = data_frame[data_frame.columns.drop(list(data_frame.filter(regex='right')))]
        data_frame2 = data_frame[data_frame.columns.drop(list(data_frame.filter(regex='left')))]

        data_frame7 = data_frame1.sort_index(axis=1)
        header=data_frame7.columns.tolist()
        data_frame8 = data_frame2.sort_index(axis=1)
        data_frame9 = data_frame8.rename(columns=dict(zip(data_frame8.columns,header)))

        #combined = [data_frame7, data_frame9]
        #result = pd.concat(combined)
        final = data_frame7.append(data_frame9).sort_values('0rank').drop_duplicates(subset=[leftfield],keep='first')

        data_final = pd.merge(final, joindataframe, how='left',left_on=final[leftfield], right_on=joindataframe[columntocheckduplicate],
        left_index=False, right_index=False)
        data_final2 = data_final[data_final.columns.drop(list(data_final.filter(regex='left')))]
        data_final2 = data_final2.sort_index(axis=1)

        import base64
        from io import BytesIO
        st.dataframe(data_final2)

        def filedownload(df):              # Function Code snippet for downloading as .csv file (Source: https://discuss.streamlit.io/t/how-to-download-file-in-streamlit/1806 )
          csv = df.to_csv(index=False)
          b64 = base64.b64encode(csv.encode()).decode()  # strings <-> bytes conversions
          href = f'<a href="data:file/csv;base64,{b64}" download="result.csv">Download .csv file</a>'
          return href
        st.markdown(filedownload(data_final2), unsafe_allow_html=True)

        def to_excel(df):
          output = BytesIO()
          writer = pd.ExcelWriter(output, engine='xlsxwriter')
          df.to_excel(writer, sheet_name='Sheet1')
          writer.save()
          processed_data = output.getvalue()
          return processed_data

        def get_table_download_link(df):
          """Generates a link allowing the data in a given panda dataframe to be downloaded
          in:  dataframe
          out: href string
          """
          val = to_excel(df)
          b64 = base64.b64encode(val)  # val looks like b'...'
          return f'<a href="data:application/octet-stream;base64,{b64.decode()}" download="result.xlsx">Download .xlsx file</a>' # decode b'abc' => abc

          
        st.markdown(get_table_download_link(data_final2), unsafe_allow_html=True)

        st.success('Done!')

except:
  pass


