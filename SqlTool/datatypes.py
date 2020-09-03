class INT:
    def __new__(cls,type='INT'):
        """INT、SMALLINT、MEDIUMINT、BIGINT、TINYINT"""
        return type

class STR:
    def __new__(cls,type='VARCHAR'):
        return f"{type}"