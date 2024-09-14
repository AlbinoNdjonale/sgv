def format_number(number: int, money = "00 KZ"):
    digs = [dig for dig in str(number)]
    digs.reverse()
    res = []
    
    c = 0
    for dig in digs:
        res.append(dig)
        c += 1
        if c == 3:
            c = 0
            res.append(" ")
    
    res.reverse()
    res = "".join(res)       
    return res+"."+money