'''
    Class to manage dates and times
'''

from datetime import datetime
from dateutil import tz

class DateUtil():
    '''
        Convenient functions to manipulate dates,
        especially conversion from utc time to local time. 
    '''
    
    def convert_utc_to_local(utc_time):
        from_zone = tz.tzutc()
        to_zone = tz.tzlocal()
        utc = datetime.strptime(utc_time, '%Y-%m-%d %H:%M:%S')
        utc = utc.replace(tzinfo=from_zone)
        local = utc.astimezone(to_zone)
        return local.strftime('%Y-%m-%d, %H:%M:%S')
    
    def convert_utc_to_local_HM(utc_time):
        from_zone = tz.tzutc()
        to_zone = tz.tzlocal()
        utc = datetime.strptime(utc_time, '%Y-%m-%d %H:%M:%S')
        utc = utc.replace(tzinfo=from_zone)
        local = utc.astimezone(to_zone)
        return local.strftime('%H:%M')
