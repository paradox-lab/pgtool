dtypes={
    str:{
        'go':['string','byte','rune']},
    list:{
        'go':['[]'],
        'javascript':'[]'}
    }


lib={
    'io':{'go':"io/ioutil"}}

sitepk={
    'azure.storage.blob':{'go':"github.com/Azure/azure-storage-blob-go/azblob"},
    'openpyxl':{'go':"github.com/360EntSecGroup-Skylar/excelize"},
    'cx_oracle':{'go':"github.com/mattn/go-oci8",
                 'java':"oracle.jdbc.driver.OracleDriver"}
}

func={
    print:{
        'go':'fmt.Println',
        'javascript':['document.wirte','console.log']}}
