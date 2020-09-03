from string import Template

def VAR(varname,default=None):
    text = "var ${varname} "
    if default:
        text+="=${default}"