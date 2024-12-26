# startup script:
# cd C:\Users\NZ\OneDrive\Codes\UM2
# streamlit run AIT_AA_GUI.py
# import streamlit as st
import pandas as pd
import os.path

# functions ----------------------
def file_is_available(file):
    return os.path.isfile(file)
def make_folder_when_not_available(file):
    path = os.path.dirname(file)
    if not os.path.exists(path):
        os.makedirs(path)
def import_file(file,cols_index=[],cols_datetime=[],cols_date=[]):
    df = pd.DataFrame(columns=cols_index)
    if(file_is_available(file)):
        cols_datetime = list(set(cols_datetime)|set(cols_date))
        df = pd.read_csv(file, parse_dates=cols_datetime)
    if(len(df)>0):
        for col in cols_date:
            df[col] = df[col].dt.date
    if(len(cols_index)>0):
        df.set_index(cols_index,inplace=True)
    return df
def export_file(df,file,cols_index):
    if(len(df)>0):
        make_folder_when_not_available(file)
        df.to_csv(file,index=len(cols_index)>0)

# data ---------------------------------------
# df_items = pd.read_csv('Items.csv')
# df_batch = pd.read_csv('Batch.csv')
# df_po = pd.read_csv('PurchaseOrder.csv')
# df_trans = pd.read_csv('Transaction.csv')


# object structure ----------------------------------
# Base object for specific datatype, include functions: get_file_name, import, export =========================================
class FileObj:
    def __repr__(self):
        return f"{self.name}"
    def __init__(self):
        self.name = 'FileObj'
        self.cols_index = []
        self.cols_datetime = []
        self.cols_date = []
    def get_file(self):
        return ''+self.key
    def set_key(self,key):
        self.key = ''# variable filename
        return self
    def import_file(self):
        df = import_file(self.get_file(), self.cols_index, self.cols_datetime, self.cols_date)
        # df = self.import_postprocessing(df)
        return df
    def export_file(self, df):
        export_file(df, self.get_file(), self.cols_index)
        
class DataFile:
    def __repr__(self):
        return f"{self.name}"
    def __init__(self):
        self.name = 'DataFile'
        self.file_item = self.File_Item(self)
        self.file_batch = self.File_Batch(self)
        self.file_purchaseorder = self.File_PurchaseOrder(self)
        self.file_sale = self.File_Sale(self)
    class File_Item(FileObj):
        def __init__(self, datafile):
            self.name = 'File_Item'
            self.datafile = datafile
            self.cols_index = []
            self.cols_datetime = []
            self.cols_date = []
        def get_file(self):
            return 'Data\\Item.csv'
    class File_Batch(FileObj):
        def __init__(self, datafile):
            self.name = 'File_Batch'
            self.datafile = datafile
            self.cols_index = []
            self.cols_datetime = []
            self.cols_date = ['ExpiryDate']
        def get_file(self):
            return 'Data\\Batch.csv'
    class File_PurchaseOrder(FileObj):
        def __init__(self, datafile):
            self.name = 'File_PurchaseOrder'
            self.datafile = datafile
            self.cols_index = []
            self.cols_datetime = []
            self.cols_date = ['PurchaseOrderDate','ArrivalDate']
        def get_file(self):
            return 'Data\\PurchaseOrder.csv'
    class File_Sale(FileObj):
        def __init__(self, datafile):
            self.name = 'File_Sales'
            self.datafile = datafile
            self.cols_index = []
            self.cols_datetime = []
            self.cols_date = ['Date']
        def get_file(self):
            return 'Data\\Sale.csv'
    
class Company:
    def __repr__(self):
        return f"{self.name}"
    def __init__(self):
        self.name = 'Company'
        
        # KPIs
        self.NrItems = 0
        self.Revenue = 0.0
        
        # data files
        self.datafile = DataFile()
        
        # relations: child objects
        self.items = {}
        
        # load initial data
        self.load_items()
        self.load_batchs()
        self.load_sales()
        self.load_pos()
        
    def calculate_on_new_item(self):
        self.calc_NrItems()
    def calc_NrItems(self):
        self.NrItems = len(self.items.values())
    def load_items(self):
        df = self.datafile.file_item.import_file()
        for index, row in df.iterrows():
            self.Item(self,row['Code'], row['Name'],row['Type'],row['RefPrice'],row['UOM'])
    def load_batchs(self):
        df = self.datafile.file_batch.import_file()
        for index, row in df.iterrows():
            self.Batch(self,row['ItemCode'], row['BatchID'],row['ExpiryDate'])
    def load_sales(self):
        df = self.datafile.file_sale.import_file()
        for index, row in df.iterrows():
            self.Sale(self,row['ItemCode'],row['BatchID'],row['Date'],row['PricePerUnit'],row['UnitSold'])
    def load_pos(self):
        df = self.datafile.file_purchaseorder.import_file()
        for index, row in df.iterrows():
            self.PurchaseOrder(self,row['ItemCode'],row['BatchID'],row['PurchaseOrderDate'],row['ArrivalDate'],row['PO_Qty'],row['LeadTime'],row['CostPerUnit'])
    def get_item(self,itemcode):
        obj = None
        if(itemcode in self.items.keys()):
            obj = self.items[itemcode]
        return obj
    def get_batch(self,itemcode,batchid):
        obj = None
        item = self.get_item(itemcode)
        if(item != None and batchid in item.batchs.keys()):
            obj = item.batchs[batchid]
        return obj
    
    def get_all_batchs(self):
        objs = []
        for item in self.items.values():
            for obj in item.batchs.values():
                objs.append(obj)
        return objs
    def get_all_sales(self):
        objs = []
        for item in self.items.values():
            for obj in item.sales:
                objs.append(obj)
        return objs
    def get_all_pos(self):
        objs = []
        for item in self.items.values():
            for obj in item.pos:
                objs.append(obj)
        return objs
    def get_all_itemdays(self):
        objs = []
        for item in self.items.values():
            for obj in item.itemdays.values():
                objs.append(obj)
        return objs
    
    def get_df(self,objs):
        data = [obj.get_data() for obj in objs]
        df = pd.DataFrame(data)
        return df
    def get_df_items(self):
        return self.get_df(self.items.values())
    def get_df_batchs(self):
        objs = self.get_all_batchs()
        return self.get_df(objs)
    def get_df_sales(self):
        objs = self.get_all_sales()
        return self.get_df(objs)
    def get_df_pos(self):
        objs = self.get_all_pos()
        return self.get_df(objs)
    def get_df_itemdays(self):
        objs = self.get_all_itemdays()
        for obj in objs:
            obj.calculate()
        return self.get_df(objs)
    
    class Item:
        def __repr__(self):
            return f"Item:{self.Code}"
        def __init__(self,company,code,name,type_,ref_price,uom):
            self.company=company
            
            # attributes
            self.Code=code
            self.Name=name
            self.Type=type_
            self.ReferencePrice=ref_price
            self.UOM=uom
            
            # declarative attributes
            self.Revenue = 0.0
            self.UnitSold = 0
            
            # relations
            self.batchs = {}
            self.sales = []
            self.pos = []
            self.itemdays = {}
            self.add_to_company()
            
        def get_filter_attributes(self): 
            return ['company','batchs','sales','pos','itemdays']
        def add_to_company(self):
            self.company.items[self.Code]=self
            self.company.calculate_on_new_item()
        def get_add_itemday(self,date):
            obj = self.get_itemday(date)
            if(obj == None):
                obj = self.company.ItemDay(self.company, self.Code, date)
            
            return obj
            
        def get_itemday(self,date):
            obj = None
            if(date in self.itemdays.keys()): obj = self.itemdays[date]
            return obj
        def get_df_batchs(self):
            objs = [batch for batch in self.batchs.values()]
            return self.company.get_df(objs) 
        def get_df_sales(self):
            objs = self.sales
            return self.company.get_df(objs) 
        def get_df_pos(self):
            objs = self.pos
            return self.company.get_df(objs) 
        def get_df_itemdays(self):
            objs = self.itemdays.values()
            for obj in objs:
                obj.calculate()
            df = self.company.get_df(objs)
            df = df.sort_values(by='Date')
            df['Inventory'] = df['InventoryChange'].cumsum()
            return df
        
        # COMMON METHODS -------------------------
        def get_data(self):
            filter_attributes = self.get_filter_attributes()
            return {name:value for name,value in vars(self).items() if not name in filter_attributes}    
        
    class Batch:
        def __repr__(self):
            return f"Batch:{self.ItemCode}-{self.BatchID}"
        def __init__(self,company,itemcode,batchid,expiry):
            self.company = company
            self.item = None
            
            # attributes
            self.ItemCode = itemcode
            self.BatchID = batchid
            self.ExpiryDate = expiry
            
            # declarative attributes
            self.Revenue = 0.0
            self.UnitSold = 0
            
            self.sales = []
            self.pos = []
            self.add_relations()
        def add_relations(self):
            if(self.ItemCode in self.company.items.keys()):
                self.item=self.company.items[self.ItemCode]
                self.item.batchs[self.BatchID]=self
        def get_filter_attributes(self):
            return ['company','item','sales','pos']
        # COMMON METHODS -------------------------
        def get_data(self):
            filter_attributes = self.get_filter_attributes()
            return {name:value for name,value in vars(self).items() if not name in filter_attributes}   
        
    class Sale:
        def __repr__(self):
            return f"Sale:{self.ID}"
        def __init__(self, company, ItemCode, BatchID, Date, PricePerUnit, UnitSold):
            self.company = company
            self.item = None
            self.batch = None
            
            self.ID = -1
            
            # attributes
            self.ItemCode = ItemCode
            self.BatchID = BatchID
            self.Date = Date
            self.PricePerUnit = PricePerUnit
            self.UnitSold = UnitSold
            
            self.Revenue = PricePerUnit * self.UnitSold
            
            self.add_relations()
        def get_filter_attributes(self): 
            return ['company','item','batch']
        
        def add_relations(self):
            item = self.company.get_item(self.ItemCode)
            batch = self.company.get_batch(self.ItemCode,self.BatchID)
            if(item!=None and batch != None):
                self.item = item
                self.batch = batch
                
                self.ID = len(self.item.sales)
                self.item.sales.append(self)
                self.batch.sales.append(self)
                
                itemday = self.item.get_add_itemday(self.Date)
                if(itemday!=None):
                    itemday.sales.append(self)
                    
        # COMMON METHODS -------------------------
        def get_data(self):
            filter_attributes = self.get_filter_attributes()
            return {name:value for name,value in vars(self).items() if not name in filter_attributes} 
    class PurchaseOrder:
        def __repr__(self):
            return f"Sale:{self.ID}"
        def __init__(self, company, ItemCode, BatchID, PurchaseOrderDate, ArrivalDate, PO_Qty, LeadTime, CostPerUnit):
            self.ID = -1
            self.company = company
            self.item = None
            self.batch = None
            
            self.ItemCode = ItemCode
            self.BatchID = BatchID
            self.PurchaseOrderDate = PurchaseOrderDate
            self.ArrivalDate = ArrivalDate
            self.PO_Qty = PO_Qty
            self.LeadTime = LeadTime
            self.CostPerUnit = CostPerUnit
            
            self.add_relations()
        def get_filter_attributes(self): 
            return ['company','item','batch']
        def add_relations(self):
            item = self.company.get_item(self.ItemCode)
            batch = self.company.get_batch(self.ItemCode,self.BatchID)
            if(item!=None and batch != None):
                self.item = item
                self.batch = batch
                
                self.ID = len(self.item.pos)
                self.item.pos.append(self)
                self.batch.pos.append(self)
                
                itemday = self.item.get_add_itemday(self.ArrivalDate)
                if(itemday!=None):
                    itemday.pos.append(self)
                    
        
        # COMMON METHODS -------------------------
        def get_data(self):
            filter_attributes = self.get_filter_attributes()
            return {name:value for name,value in vars(self).items() if not name in filter_attributes} 
    class ItemDay:
        def __repr__(self):
            return f"ItemDay:{self.ItemCode}-{self.Date}"
        def __init__(self,company,ItemCode,Date):
            self.company = company
            self.item = None
            
            self.ItemCode = ItemCode
            self.Date = Date
            # declarative attribute
            self.NrPOs=0
            self.NrSales=0
            self.UnitSold=0.0
            self.UnitPurchased=0.0
            self.InventoryChange=0.0
            self.PriceSold=0.0
            self.Cost=0.0
            
            
            self.pos = []
            self.sales = []
            
            self.add_relations()
        def add_relations(self):
            item = self.company.get_item(self.ItemCode)
            if(item!=None):
                self.item = item
                
                self.item.itemdays[self.Date]=self
                
        def calculate(self):
            self.NrPOs=len(self.pos)
            self.NrSales=len(self.sales)
            unitpurchased=0.0
            unitsold=0.0
            for po in self.pos:
                unitpurchased=unitpurchased+po.PO_Qty
            for sale in self.sales:
                unitsold=unitsold+sale.UnitSold
            
            self.UnitSold=unitsold
            self.UnitPurchased=unitpurchased
            self.InventoryChange=unitpurchased-unitsold
            
        def get_filter_attributes(self): 
            return ['company','item','pos','sales']
        # COMMON METHODS -------------------------
        def get_data(self):
            filter_attributes = self.get_filter_attributes()
            return {name:value for name,value in vars(self).items() if not name in filter_attributes} 
            
    class Day:
        def __repr__(self):
            return f"{self.name}"
        def __init__(self):
            self.name = 'Day'
    
    
# main ---------------------
if __name__ == "__main__":
    c = Company()
    
    df_items = c.datafile.file_item.import_file()
    df_batch = c.datafile.file_batch.import_file()
    df_po = c.datafile.file_purchaseorder.import_file()
    df_sales = c.datafile.file_sale.import_file()
    df_items_c = c.get_df_items()
    df_batchs_c = c.get_df_batchs()
    df_sales_c = c.get_df_sales()
    df_pos_c = c.get_df_pos()
    df_itemdays_c = c.get_df_itemdays()
    df_batchs_item = c.items[1].get_df_batchs()
    df_sales_item = c.items[1].get_df_sales()
    df_pos_item = c.items[1].get_df_pos()
    df_itemdays_item = c.items[1].get_df_itemdays()
    
    
    kpi_nr_items = c.NrItems
