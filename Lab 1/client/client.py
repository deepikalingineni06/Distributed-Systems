#importing required packages
import requests
import json
#getting data from server1
try:
    dataFromServerA = requests.get("http://localhost:8080")
    print("server A connected")
    dataFromServerA = dataFromServerA.text
except:
    print("Not able to get server A info")

#Organising data from servers 
try:
    fina = eval(dataFromServerA)
    fina_body = fina["body"]
    fina_sizes = fina["sizes"]
    fina_times = fina['times']
    #making a dictionary with keys as file names and values as sizes and last_modified dates
    def arranger(data):
        count = 0
        dictionary = {}
        for i in data:
            dictionary[i] = [fina_sizes[count],fina_times[count]] 
            count += 1
        return dictionary

    fina_dict = arranger(fina_body)
    
    #sorting the data in alphabetical order
    def sorter_and_printer(data1,data_dict):
        data1 = sorted(data1,key=str.lower)
        count = 1
        for i in data1:
            print(f"{count}. {i}\t{round((data_dict[i][0])/1024,3)}kb\t{data_dict[i][1]} ")
            count += 1

    sorter_and_printer(fina_body,fina_dict)
except:
    print("Restart servers")


