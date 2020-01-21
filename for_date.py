import datetime


# now_date=datetime.date.today()
# one_day=datetime.timedelta(days=1)
# yesterday=now_date-one_day
# print('today',now_date)
# print('yerterday',yesterday)
def getdate(start_date):
    t_date=datetime.datetime.strptime(start_date,r"%Y-%m-%d")
    now=datetime.date.today()
    str_now=now.strftime(r'%Y-%m-%d')
    one_day=datetime.timedelta(days=1)
    #str_now_date=now_date.strftime(r"%Y-%m-%d")
    if str_now>=start_date:
        print(start_date)
        t_date+=one_day
        next_date=t_date.strftime(r'%Y-%m-%d')
        

        getdate(next_date)
    
    else:
        end_date=t_date-one_day
        print('end',end_date.strftime(r"%Y-%m-%d"))


if __name__=="__main__":
    start_date='2019-08-28'
    getdate(start_date)
