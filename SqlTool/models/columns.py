class STR:
    def __init__(self,length):
        self.length=length
    def __str__(self):
        return f'${{STR}}({self.length})'

class INT:
    def __str__():
        return f"${{INT}}"


build_col={
    'Email':STR(128),
    'MobilePhone':INT,
    'username':STR(128)    
    }

