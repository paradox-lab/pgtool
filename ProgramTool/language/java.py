from string import Template
from ProgramTool.transfer import dtypes

def TRY(**kwargs):
    template="""try {  
	// 可能会发生异常的程序代码
	${statement}  	
} catch (Type1 id1){  
	// 捕获并处置try抛出的异常类型Type1  
} catch (Type2 id2){  
	 //捕获并处置try抛出的异常类型Type2  
}finally {
	//结束时处理的程序代码，该语句可选
	}
    """
    T=Template(template)

    return T.safe_substitute(**kwargs)