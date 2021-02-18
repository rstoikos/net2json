import glob
import os
import json
from ipaddress import ip_network 

def sameNetwork(IP1, IP2): 
    
    a = ip_network(IP1, strict = False).network_address 
    b = ip_network(IP2, strict = False).network_address 
    if(a == b) : 
        return True 
  
    else : 
        return False

def index_of_specific_ip(search_term): # since we have a dictionary that contains a list that has dictonaries 
   for key, value in topology_dict.items():  #that hold the id and name if each router
      if "nodes" in key:
            list_of_nodes = value # we want to grab the nodes list
            a = list(filter(lambda name: name['name'] == search_term, list_of_nodes)) # search for the value we want inside
 the list
            x = a[0]  # take the dictonary that matches our search term
            y = x.get('id') # return the id
            return(y)  


topology_dict = {'nodes': [], 'links': []}
host_id = 0
host_id2 = 0


for filename in glob.glob('*.temp_json'):  # fill topology_dict with all nodes
   with open(os.path.join(os.curdir, filename), 'r') as json_file:
      data = json.load(json_file) 
      topology_dict['nodes'].append({
         'id': host_id,
         'name': filename,
            })
   host_id +=1

  

for filename in glob.glob('*.temp_json'):
   with open(os.path.join(os.curdir, filename), 'r') as json_file:
      host_id = index_of_specific_ip(filename)
      data = json.load(json_file) 
      for key, value in data.items():
         for filename1 in glob.glob('*.temp_json'):  
            with open(os.path.join(os.curdir, filename1), 'r') as json_file1:
               host_id2 = index_of_specific_ip(filename1)
               if filename == filename1:
                  pass
               else:
                  data1 = json.load(json_file1)
                  for key, value1 in data1.items():
                     if sameNetwork(value,value1):
                        topology_dict['links'].append({
                        'source' : host_id,
                        'target': host_id2,
                     })
   os.remove(filename)

v = json.dumps(topology_dict, indent=4)
print(v)