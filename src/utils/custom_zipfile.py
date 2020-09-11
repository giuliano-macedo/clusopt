import zipfile
import io
import pandas as pd
import json
from datetime import datetime

class IOStringToBytes(io.IOBase):
    def __init__(self,file_handler,encoding="utf-8"):
        self.file_handler=file_handler
        self.encoding=encoding
    
    def write(self,string):
        self.file_handler.write(string.encode(self.encoding))
    
    def close(self):
        self.file_handler.close()

class CustomZipFile:
    def __init__(self,fname):
        self.zf=zipfile.ZipFile(fname,"w")

    def __enter__(self):
        return self

    def __exit__(self,*exc_info):
        self.close()

    def __create_info(self,name):
        date=datetime.now()
        return zipfile.ZipInfo(
            filename=name,
            date_time=(date.year,date.month,date.day,date.hour,date.minute,date.second)
        )

    def add_json(self,fname:str,obj,encoding="utf-8",ensure_ascii=False,indent=None):
        with self.zf.open(self.__create_info(fname),"w") as f:
            json.dump(obj,IOStringToBytes(f,encoding),ensure_ascii=ensure_ascii,indent=indent)

    def add_dataframe(self,fname:str,df:pd.DataFrame,encoding="utf-8",index=None,header=True):
        with self.zf.open(self.__create_info(fname),"w") as f:
            df.to_csv(IOStringToBytes(f,encoding),index=index,header=header)

    def add_txt(self,fname:str,string:str,encoding="utf-8"):
        with self.zf.open(self.__create_info(fname),"w") as f:
            f.write(string.encode(encoding))

    def close(self):
        self.zf.close()
