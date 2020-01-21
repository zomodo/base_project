import datetime
import calendar
year=datetime.datetime.now().year
month=datetime.datetime.now().month
p=calendar.monthrange(year,month-1)
print(p[1])