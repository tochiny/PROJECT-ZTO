class Organize:
    
    def __init__(self):
        super().__init__()
    
    def abbreviationLetter(self, listData: list, limit: int = 10):
        number = 1
        n = 1
        listReturn = {}
        listReturn[str(number)] = {}
        for data in listData:
            if len(listReturn[str(number)]) == limit:
                number += 1
                listReturn[str(number)] = {}
            listReturn[str(number)][str(data)] = str(n)
            n += 1
        return listReturn , number, n