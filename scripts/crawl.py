"""
    
     https://www.bis.org/cbspeeches/index.htm?m=256&cbspeeches_page_length=25&authors=2860

     prepend BOM  
     Powershell
     Get-Content ".\ecb_council_members.csv" | Out-File ".\ecb_council_members-bom.csv" -Encoding utf8
     Format-Hex ".\ecb_council_members-bom.csv" -Count 3

    for each row in the  csv semicolon delimited CSV file
     call 
     https://www.bis.org/cbspeeches/index.htm
     and enter the  name from the csv  file.
     into the field "Autor".
     
     Then the page should redirect to another URL.

     I only want the resulting URL - not the content

     For example if one enters 'Luis de Guindos' the result URL is

     https://www.bis.org/cbspeeches/index.htm?m=256&authors=2860&cbspeeches_page_length=25     
     
"""