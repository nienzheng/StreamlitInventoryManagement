# startup script:
# cd C:\Users\NZ\OneDrive\Codes\UM2
# streamlit run AIT_AA_GUI.py








import AIT_AA_OOP as oop
import streamlit as st
import pandas as pd
import os.path
from st_aggrid import AgGrid, GridOptionsBuilder, ColumnsAutoSizeMode#, GridUpdateMode
from pyecharts.charts import Line
from pyecharts import options as opts
from streamlit_echarts import st_pyecharts
import datetime as dt

# GUI Functions
def show_list_selectable(df,list_name='',is_single_selection=True):
    selected_rows = []
    if(len(df)>0):
        selection_mode = 'single'
        if(not is_single_selection):
            selection_mode = 'multiple'
        gd = GridOptionsBuilder.from_dataframe(df)
        gd.configure_pagination(enabled=True,paginationPageSize=10, paginationAutoPageSize=False)
        gd.configure_side_bar()
        gd.configure_default_column(editable=False,groupable=False)
        gd.configure_selection(selection_mode=selection_mode,use_checkbox=False)
        gridoptions = gd.build()
        selected_rows = AgGrid(df
                            , gridOptions=gridoptions
                            , fit_columns_on_grid_load=True
                            , ColumnsAutoSizeMode = ColumnsAutoSizeMode.FIT_ALL_COLUMNS_TO_VIEW
                            )["selected_rows"]
    return selected_rows

def draw_line_chart(df,title,x_label,y_labels,ma_periods=[]):
    for ma_period in ma_periods:
        for y_label in y_labels:
            label = y_label+'_MA'+str(ma_period)
            df[label]=df[y_label].rolling(window=ma_period).mean()
            if(df[y_label].dtype=='int64' or df[y_label].dtype=='int32'):
                df[label]=df[label].fillna(0).astype(int)
            else:
                df[label]=df[label].round(2)
    
    # line charts - MA
    x = []
    if(x_label=='index'):
        x = df.index.tolist()
    else:
        x = df[x_label].tolist()
        
    c = Line().add_xaxis(x)
    for y_label in y_labels:
        c = c.add_yaxis(y_label, df[y_label].tolist())
        for ma_period in ma_periods:
            label = y_label+'_MA'+str(ma_period)
            c = c.add_yaxis(label, df[label].tolist())
        
    c = c.set_global_opts(title_opts=opts.TitleOpts(title=title)
                          , datazoom_opts=[opts.DataZoomOpts(xaxis_index=0,range_start=0,range_end=100)]
                          , tooltip_opts=opts.TooltipOpts(
                              trigger="axis"
                              , axis_pointer_type="cross"
                              , background_color="rgba(245, 245, 245, 0.8)"
                              , border_width=1
                              , border_color="#ccc"
                              , textstyle_opts=opts.TextStyleOpts(color="#000")
                              )
                          , yaxis_opts=opts.AxisOpts(
                              type_="value"
                              , min_="dataMin" # Set minimum to data's minimum value
                              , max_="dataMax" # Set maximum to data's maximum value
                              )
                          )
    st_pyecharts(c,height="300px")
# object structure



# main ---------------------------------------
c = oop.Company()

st.set_page_config(
    page_title="INVENTORY MANAGEMENT",
    page_icon=":chart_with_upwards_trend:", 
    layout="wide"
    )
cols = st.columns(2)

if st.sidebar.button('Add Sales'):
    date = dt.date(2024, 12, 25)
    c.PurchaseOrder(c,1,1,date,date,1000,3,40)
    c.PurchaseOrder(c,2,1,date,date,1000,3,40)
    c.datafile.file_purchaseorder.export_file(c.get_df_pos())

df_items = c.get_df_items()
df_batch = c.get_df_batchs()
df_po = c.get_df_pos()
df_sales = c.get_df_sales()
# df_items = pd.read_csv('Items.csv')
# df_batch = pd.read_csv('Batch.csv')
# df_po = pd.read_csv('PurchaseOrder.csv')
# df_trans = pd.read_csv('Transaction.csv')
# cols[0].write(df_items)
# cols[0].write(df_batch)
# cols[0].write(df_po)
# cols[0].write(df_sales)

selected_item = []
with cols[0]: selected_item = show_list_selectable(df_items)
# if(len(selected_item)>0): cols[1].write(selected_item)
cols[0].write(df_batch)
cols[0].write(df_po)
cols[0].write(df_sales)

with cols[1]:
    if(len(selected_item)>0): st.write(str(selected_item[0]['Code']) + ' ' + selected_item[0]['Name'])
    filter_df_batch=df_batch[df_batch['ItemCode']==selected_item[0]['Code']]
    st.write(filter_df_batch)
    filter_df_po=df_po[df_po['ItemCode']==selected_item[0]['Code']]
    st.write(filter_df_po)
    filter_df_trans=df_sales[df_sales['ItemCode']==selected_item[0]['Code']]
    st.write(filter_df_trans)
    
    df_itemdays = c.get_item(selected_item[0]['Code']).get_df_itemdays()
    st.write(df_itemdays)
    draw_line_chart(df_itemdays, 'Inventory of '+ selected_item[0]['Name'], 'Date', ['Inventory','InventoryChange','UnitSold','UnitPurchased'])
    



# # libraries
# import streamlit as st
# import pandas as pd
# import os.path
# from st_aggrid import AgGrid, GridOptionsBuilder, ColumnsAutoSizeMode#, GridUpdateMode

# # functions
# def file_is_available(file):
#     return os.path.isfile(file)
# def make_folder_when_not_available(file):
#     path = os.path.dirname(file)
#     if not os.path.exists(path):
#         os.makedirs(path)
# def import_file(file,cols_index=[],cols_datetime=[],cols_date=[]):
#     df = pd.DataFrame(columns=cols_index)
#     if(file_is_available(file)):
#         cols_datetime = list(set(cols_datetime)|set(cols_date))
#         df = pd.read_csv(file, parse_dates=cols_datetime)
#     if(len(df)>0):
#         for col in cols_date:
#             df[col] = df[col].dt.date
#     if(len(cols_index)>0):
#         df.set_index(cols_index,inplace=True)
#     return df
# def export_file(df,file,cols_index):
#     if(len(df)>0):
#         make_folder_when_not_available(file)
#         df.to_csv(file,index=len(cols_index)>0)

# # object structure
# # Base object for specific datatype, include functions: get_file_name, import, export =========================================
# class FileObj:
#     def __repr__(self):
#         return f"{self.name}"
#     def __init__(self):
#         self.name = 'FileObj'
#         self.cols_index = []
#         self.cols_datetime = []
#         self.cols_date = []
#     def get_file(self):
#         return ''+self.key
#     def set_key(self,key):
#         self.key = ''# variable filename
#         return self
#     def import_file(self):
#         df = import_file(self.get_file(), self.cols_index, self.cols_datetime, self.cols_date)
#         # df = self.import_postprocessing(df)
#         return df
#     def export_file(self, df):
#         export_file(df, self.get_file(), self.cols_index)
# class Company:
#     def __repr__(self):
#         return f"{self.name}"
#     def __init__(self):
#         self.name = 'Company'
        
#         self.file_items = self.File_Item(self)
        
#         self.items = []
        
#         self.load_items()
#         # self.create_items()
        
#         # KPIs
#         self.NrItems = 0
#     def calculate_on_new_item(self):
#         self.calc_NrItems()
        
#     def calc_NrItems(self):
#         self.NrItems = len(self.items)
        
#     def load_items(self):
#         df = self.file_items.import_file()
#         for index, row in df.iterrows():
#             self.Item(self, row['Name'],row['Type'],row['ReferencePrice'],row['UOM'])
        
#     def create_items(self):
#         self.Item(self, 'Apple')
#         self.Item(self, 'Orange')
        
#         self.file_items.export_file(self.get_df_items())
        
#     def get_df(self,objs):
#         # for obj in objs:
#         #     obj.calculate()
#         data = [obj.get_data() for obj in objs]
#         df = pd.DataFrame(data)
#         return df
#     def get_df_items(self):
#         return self.get_df(self.items)
    
#     class File_Item(FileObj):
#         def __init__(self, company):
#             self.name = 'File_Item'
#             self.company = company
#             self.cols_index = []
#             self.cols_datetime = []
#             self.cols_date = []
#         def get_file(self):
#             return 'Data\\items.csv'
#     class File_Batch(FileObj):
#         def __init__(self, company):
#             self.name = 'File_Batch'
#             self.company = company
#             self.cols_index = []
#             self.cols_datetime = []
#             self.cols_date = []
#         def get_file(self):
#             return 'Data\\batch.csv'
        
    
#     class Item:
#         def __repr__(self):
#             return f"{self.name}"
#         def __init__(self,company,name,type_='General',ref_price=0.0,uom='Unit'):
#             self.ID=len(company.items)
#             self.Name=name
#             self.Type=type_
#             self.ReferencePrice=ref_price
#             self.UOM=uom
            
#             self.add_to_company(company)
#         def add_to_company(self,company):
#             self.company=company
#             company.items.append(self)
#             company.calculate_on_new_item()
#         def get_filter_attributes(self): 
#             return ['company']
#         # COMMON METHODS -------------------------
#         def get_data(self):
#             filter_attributes = self.get_filter_attributes()
#             return {name:value for name,value in vars(self).items() if not name in filter_attributes}    
        
#     class ItemBatch:
#         def __repr__(self):
#             return f"{self.name}"
#         def __init__(self):
#             self.name = 'ItemBatch'
#     class Day:
#         def __repr__(self):
#             return f"{self.name}"
#         def __init__(self):
#             self.name = 'Day'
#     class ItemDay:
#         def __repr__(self):
#             return f"{self.name}"
#         def __init__(self):
#             self.name = 'ItemDay'
#     class Transaction:
#         def __repr__(self):
#             return f"{self.name}"
#         def __init__(self):
#             self.name = 'Transaction'

# # GUI Functions
# def show_list_selectable(df,list_name='',is_single_selection=True):
#     selected_rows = []
#     if(len(df)>0):
#         selection_mode = 'single'
#         if(not is_single_selection):
#             selection_mode = 'multiple'
#         gd = GridOptionsBuilder.from_dataframe(df)
#         gd.configure_pagination(enabled=True,paginationPageSize=10, paginationAutoPageSize=False)
#         gd.configure_side_bar()
#         gd.configure_default_column(editable=False,groupable=False)
#         gd.configure_selection(selection_mode=selection_mode,use_checkbox=False)
#         gridoptions = gd.build()
#         selected_rows = AgGrid(df
#                             , gridOptions=gridoptions
#                             , fit_columns_on_grid_load=True
#                             , ColumnsAutoSizeMode = ColumnsAutoSizeMode.FIT_ALL_COLUMNS_TO_VIEW
#                             )["selected_rows"]
#     return selected_rows

# c = Company()

# st.set_page_config(
#     page_title="INVENTORY MANAGEMENT",
#     page_icon=":chart_with_upwards_trend:", 
#     layout="wide"
#     )
# # screen: item-inventory
# # st.write('Items')
# list_item = st.empty()
# list_batch = st.empty()
# # with list_items: selected_item=show_list_selectable(c.get_df_items())
# # list_items.write(c.get_df_items())

# # st.write(c.get_df_items())
# if st.button('Add item'):
#     c.create_items()
# # list_items.write(c.get_df_items())
# with list_item: selected_item=show_list_selectable(c.get_df_items(),'Items')
# # with list_item: selected_item=st.dataframe(c.get_df_items(),on_select='rerun',selection_mode=['single-row'])
# # selected_item = show_list_selectable(c.get_df_items())
# if(len(selected_item)>0): st.write(selected_item[0]['Name'])
# # if(len(selected_item)>0): st.write(selected_item)
# # st.write(c.get_df_items())
# # screen: sales (revenue) per day
# # screen: sale per item of selected day