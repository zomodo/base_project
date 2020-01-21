import pandas as pd
import numpy as np

def process(num):
    sheet='Sheet'+str(num)
    data=pd.read_excel(r"C:\Users\Administrator\Desktop\汇显11.4.xlsx",sheet_name=sheet)
    col=data.shape[1] #计算列数  行数
    row=data.shape[0]
    print('sheet%s有%s行%s列' %(str(num),row,col))
    len_nounull=data.count(axis=1)
    all=[]
    for i in range(row):
        for p in range(len_nounull[i]):
            d=str(data.ix[i][p])
            if d=='nan':
                pass
            else:
                all.append(d)


    new_data=pd.DataFrame(all,columns=['电话'])
    new_data.to_excel(writer,index=False,sheet_name=sheet)





if __name__=='__main__':
    writer=pd.ExcelWriter(r"C:\Users\Administrator\Desktop\alldata.xlsx")
    for i in range(1,60):
        print('正在处理sheet%s' %i)
        process(i)
    writer.save()
    writer.close()


