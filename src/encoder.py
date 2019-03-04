import datetime

def string_gen(n):
    dt = datetime.datetime.now()
    n = n**n
    key_val = (dt.microsecond*dt.second*dt.minute*dt.hour*dt.day*dt.month*dt.year*n)
    return hex(key_val).lstrip("0x")
