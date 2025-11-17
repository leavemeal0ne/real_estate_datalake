import re
from datetime import datetime,date,time, timezone, timedelta

class DateFormatter:
    timezone = timezone(timedelta(hours=0))
    __number_pattern = re.compile(r'\d+')
    __string_pattern = re.compile(r'[^0-9\s]+')
    __time_pattern = re.compile(r'(\d{1,2}).(\d{2})')
    __months_dict = {
        'січня':1,
        'лютого':2,
        'березня':3,
        'квітня':4,
        'травня':5,
        'червня':6,
        'липня':7,
        'серпня':8,
        'вересня':9,
        'жовтня':10,
        'листопада':11,
        'грудня':12,
    }
    __today='сьогодні'
    __yesterday='вчора'

    # сьогодні о 13.00
    # вчора о 8.46
    # 13 листопада
    @classmethod
    def date_formatter(cls,str_date):
        today_condition = not re.search(cls.__today,str_date) is None
        yesterday_condition = not re.search(cls.__yesterday,str_date) is None
        if today_condition or yesterday_condition:
            time_match = re.search(cls.__time_pattern,str_date)
            if time_match is None:
                raise ValueError("today's date value doesn't contain time info: {}".format(str_date))
            hours, minutes = time_match.groups()
            try:
                hours = int(hours)
                minutes = int(minutes) # int() can translate values with leading zero, e.g. int('01') -> 1
            except ValueError as e:
                raise e
            else:
                now_datetime = datetime.now(tz=cls.timezone)
                datetime_info = now_datetime.replace(hour=hours, minute=minutes,second=0, microsecond=0)
                if yesterday_condition:
                    datetime_info -= timedelta(days=1)
                return datetime_info
        else:
            day_number = re.search(cls.__number_pattern,str_date).group()
            try:
                day_number = int(day_number)
            except ValueError as e:
                raise e
            month = re.search(cls.__string_pattern,str_date).group()
            month_numer = cls.__months_dict[month]
            now_datetime = datetime.now(tz=cls.timezone)
            year = now_datetime.year - 1 if cls.__year_decrease_condition(now_datetime,month_numer,day_number) else now_datetime.year
            datetime_info = now_datetime.replace(year=year,month=month_numer,day=day_number,
                                                hour=0, minute=0,second=0, microsecond=0)
            return datetime_info

    @classmethod
    def __year_decrease_condition(cls,now_datetime,month_number,day_number):
        if now_datetime.month < month_number:
            return True
        elif now_datetime.month == month_number and now_datetime.day < day_number:
            return True
        else:
            return False