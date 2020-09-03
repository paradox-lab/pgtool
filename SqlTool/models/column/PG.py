from SqlTool.models.columns import STR,INT

org={
    'Division':STR(64),
    'Market':STR(64),
    'RD_NAME':STR(64),
    'Channel_Type_Code':STR(32)    
    }

banner={
    'BANNER_NAME':STR(64),
    'TOP_BANNER':INT    
    }

store={
    'STORE_SEQ':INT,
    'STORE_STATE':INT,
    'STORE_TYPE_CODE':STR(32)
    }
