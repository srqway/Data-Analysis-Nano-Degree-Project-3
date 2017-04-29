import xml.etree.ElementTree as ET  # Use cElementTree or lxml if too slow
import xml.etree.cElementTree as cET
from collections import defaultdict
import numpy as np
import sqlite3
import re
import pprint
import cerberus
import jsonschema
import csv
import codecs

#This function takes retrieves such elements so can we can make a sample file.
def get_element(osm_file, tags=('node', 'way', 'relation')):
    """Yield element if it is the right type of tag

    Reference:
    http://stackoverflow.com/questions/3095434/inserting-newlines-in-xml-file-generated-via-xml-etree-elementtree-in-python
    """
    context = iter(ET.iterparse(osm_file, events=('start', 'end')))
    _, root = next(context)
    for event, elem in context:
        if event == 'end' and elem.tag in tags:
            yield elem
            root.clear()


#This handy function is just so we can look at a couple of ways/nodes/relations
#to get an idea of structure. We can print out as many ways as we want from the sample file

def print_a_tag(filename, tag_name, num=1):
    print(tag_name+":")
    with open(filename, "r") as f:
        n=0
        for event, elem in cET.iterparse(f, events=("start",)):
            #going through each start element with the tag name of my interest
            if elem.tag==tag_name:
                #elem.items() returns list of keys and values, and a dictionary
                #looks nicer, so we will just stuff everything in a dictionary
                #and print that out to get a sense of general structure
                diction={}
                for key, value in elem.items():
                    diction[key]=value
                print(diction)
                n+=1
                if n==num:
                    break
'''
#tried this function as the reviewr suggested, but it repeats the same node
#as it keeps reading in the file everytime get_element starts...
def print_a_tag(filename, tag_name, num):
    print(tag_name+":")
    for i in range(0,num):
        node = next(audit.get_element(filename, tags=tag_name))
        print(node.attrib)
        
print_a_tag(SAMPLE_FILE,"node",3)
'''

# To make the print out function more spohisticated,
# so that  subtags are also included, to get a sense of full osm structure.
def print_a_complete_tag(filename, tag_name, num=1):
    """Clean and shape node or way XML element to Python dict"""
    print(tag_name+":")
    NODE_FIELDS = ['id', 'lat', 'lon', 'user', 'uid', 'version', 'changeset', 'timestamp']
    NODE_TAGS_FIELDS = ['id', 'key', 'value', 'type']
    WAY_FIELDS = ['id', 'user', 'uid', 'version', 'changeset', 'timestamp']
    WAY_TAGS_FIELDS = ['id', 'key', 'value', 'type']
    WAY_NODES_FIELDS = ['id', 'node_id', 'position']
    RELATION_FIELDS=['id', 'uid', 'changeset', 'timestamp', 'user', 'version']
    RELATION_TAGS_FIELDS = ['id', 'key', 'value', 'type']
    RELATION_MEMBER_FIELDS=['id',  "ref_id", "ref_to", "role"]
    
    node_attribs = {}
    way_attribs = {}
    way_nodes = []
    relation_attribs = {}
    relation_members = []
    tags = []  # Handle secondary tags the same way for both node and way elements

    # YOUR CODE HERE
    with open(filename, "r") as f:
        n=0
        for event, element in cET.iterparse(f, events=("start",)):
            if n==num:
                break
            elif tag_name=="node" and element.tag==tag_name:
                n+=1
                for item in NODE_FIELDS:
                    node_attribs[item]=element.attrib[item]
    
                for subtag in element.iter("tag"):
                    dicti={}
                    #'id', 'key', 'value', 'type'
                    dicti['id']=element.attrib['id']
                    #print subtag
                    key_holder=subtag.attrib['k']
                    if ":" in key_holder:
                        #print "addr", key_holder
                        dicti['key']=key_holder.split(":",1)[1]
                        dicti['type']=key_holder.split(":",1)[0]
                    else:
                        dicti['key']=key_holder
                        dicti['type']="regular"
                        dicti['value']=subtag.attrib['v']
                    #print(dicti)
                    tags.append(dicti)
            
                print('node:', node_attribs, 'node_tags:', tags)
            elif tag_name=="way" and element.tag==tag_name:
                n+=1
                for item in WAY_FIELDS:
                    way_attribs[item]=element.attrib[item]
    
                for subtag in element.iter("tag"):
                    dicti={}
                    #'id', 'key', 'value', 'type'
                    dicti['id']=element.attrib['id']
                    key_holder=subtag.attrib['k']
                    if ":" in key_holder:
                        #print "addr", key_holder
                        dicti['key']=key_holder.split(":",1)[1]
                        dicti['type']=key_holder.split(":",1)[0]
                    else:
                        dicti['key']=key_holder
                        dicti['type']="regular"
                        dicti['value']=subtag.attrib['v']
                    #print(dicti)
                    tags.append(dicti)

                nd_posi=1
                for subtag in element.iter("nd"):
                    dicti={}
                    #'id', 'key', 'value', 'type'
                    #print subtag
                    dicti['id']=element.attrib['id']
                    dicti["position"]=nd_posi
                    dicti['node_id']=subtag.attrib['ref']
                    nd_posi+=1
                    way_nodes.append(dicti)
            
                print('way:', way_attribs, 'way_nodes:', way_nodes, 'way_tags:', tags)
            elif tag_name=="relation" and element.tag==tag_name:
                n+=1
                for item in RELATION_FIELDS:
                    relation_attribs[item]=element.attrib[item]
    
                for subtag in element.iter("tag"):
                    dicti={}
                    #'id', 'key', 'value', 'type'
                    dicti['id']=element.attrib['id']
                    key_holder=subtag.attrib['k']
                    if ":" in key_holder:
                        #print "addr", key_holder
                        dicti['key']=key_holder.split(":",1)[1]
                        dicti['type']=key_holder.split(":",1)[0]
                    else:
                        dicti['key']=key_holder
                        dicti['type']="regular"
                        dicti['value']=subtag.attrib['v']
                    #print(dicti)
                    tags.append(dicti)

                for subtag in element.iter("member"):
                    dicti={}
                    #'id',  "ref_id", "ref_to", "role"
                    #print subtag
                    dicti['id']=element.attrib['id']
                    dicti["ref_id"]=subtag.attrib['ref']
                    dicti['ref_to']=subtag.attrib['type']
                    dicti['role']=subtag.attrib['role']
                    relation_members.append(dicti)
            
                print('relation:', relation_attribs, 'relation_members:', relation_members, 'relation_tags:', tags)

#finding strange street names:
#a regular expression that picks out the last word of a given expression:
street_type_re = re.compile(r'\b\S+\.?$', re.IGNORECASE)

expected = ["Street", "Avenue", "Boulevard", "Drive", "Court", "Place", "Square", "Lane", 
            "Road", "Trail", "Parkway", "Commons"]

#find out if street name has any weird symbols/whether or
#not it conforms to our regular expression
#and then check if the street name is in the expected list
#this function takes in one street name, and a street types dictionary
#to which at adds unusual names
def audit_street_type(street_types, street_name):
    #print("street name", street_name)
    m = street_type_re.search(street_name)
    if m:
        street_type = m.group()
        #print("street type", street_type)
        if street_type not in expected:
            street_types[street_type].add(street_name)
            
#checks a subtag to check if it holds street information
def is_street_name(elem):
    return (elem.attrib['k'] == "addr:street")

#This iterates through the xml file so we can find and check all the street names
def audit(osmfile):
    osm_file = open(osmfile, "r")
    street_types = defaultdict(set)
    for event, elem in ET.iterparse(osm_file, events=("start",)):
        if elem.tag == "node" or elem.tag == "way":
            for tag in elem.iter("tag"):
                if is_street_name(tag):
                    audit_street_type(street_types, tag.attrib['v'])
    osm_file.close()
    #print(street_types)
    return street_types

#setting up schema:
#we need a schema to validate data - we can use this to make the tables schemas in sqlite 
#(provided in the exercises):
#we only need to update this schema to add relations, also we can't use schema the 
#same way because I am using python 3

# Note: The schema is stored in a .py file in order to take advantage of the
# int() and float() type coercion functions. Otherwise it could easily stored as
# as JSON or another serialized format.

schema = {
    'node': {
        'type': 'dict',
        'schema': {
            'id': {'required': True, 'type': 'integer', 'coerce': int},
            'lat': {'required': True, 'type': 'float', 'coerce': float},
            'lon': {'required': True, 'type': 'float', 'coerce': float},
            'user': {'required': True, 'type': 'string'},
            'uid': {'required': True, 'type': 'integer', 'coerce': int},
            'version': {'required': True, 'type': 'string'},
            'changeset': {'required': True, 'type': 'integer', 'coerce': int},
            'timestamp': {'required': True, 'type': 'string'}
        }
    },
    'node_tags': {
        'type': 'list',
        'schema': {
            'type': 'dict',
            'schema': {
                'id': {'required': True, 'type': 'integer', 'coerce': int},
                'key': {'required': True, 'type': 'string'},
                'value': {'required': True, 'type': 'string'},
                'type': {'required': True, 'type': 'string'}
            }
        }
    },
    'way': {
        'type': 'dict',
        'schema': {
            'id': {'required': True, 'type': 'integer', 'coerce': int},
            'user': {'required': True, 'type': 'string'},
            'uid': {'required': True, 'type': 'integer', 'coerce': int},
            'version': {'required': True, 'type': 'string'},
            'changeset': {'required': True, 'type': 'integer', 'coerce': int},
            'timestamp': {'required': True, 'type': 'string'}
        }
    },
    'way_nodes': {
        'type': 'list',
        'schema': {
            'type': 'dict',
            'schema': {
                'id': {'required': True, 'type': 'integer', 'coerce': int},
                'node_id': {'required': True, 'type': 'integer', 'coerce': int},
                'position': {'required': True, 'type': 'integer', 'coerce': int}
            }
        }
    },
    'way_tags': {
        'type': 'list',
        'schema': {
            'type': 'dict',
            'schema': {
                'id': {'required': True, 'type': 'integer', 'coerce': int},
                'key': {'required': True, 'type': 'string'},
                'value': {'required': True, 'type': 'string'},
                'type': {'required': True, 'type': 'string'}
            }
        }
    },
    'relation': {
        'type': 'dict',
        'schema': {
            'id': {'required': True, 'type': 'integer', 'coerce': int},
            'user': {'required': True, 'type': 'string'},
            'uid': {'required': True, 'type': 'integer', 'coerce': int},
            'version': {'required': True, 'type': 'string'},
            'changeset': {'required': True, 'type': 'integer', 'coerce': int},
            'timestamp': {'required': True, 'type': 'string'}
        }
    },
    'relation_members': {
        'type': 'list',
        'schema': {
            'type': 'dict',
            'schema': {
                'id': {'required': True, 'type': 'integer', 'coerce': int},
                'ref_id': {'required': True, 'type': 'integer', 'coerce': int},
                'ref_to': {'required': True, 'type': 'string'},
                'role': {'type': 'string'}
            }
        }
    },
    'relation_tags': {
        'type': 'list',
        'schema': {
            'type': 'dict',
            'schema': {
                'id': {'required': True, 'type': 'integer', 'coerce': int},
                'key': {'required': True, 'type': 'string'},
                'value': {'required': True, 'type': 'string'},
                'type': {'required': True, 'type': 'string'}
            }
        }
    }
}

#LOWER_COLON = re.compile(r'^([a-z]|_)+:([a-z]|_)+')
PROBLEMCHARS = re.compile(r'[=\+/&<>;\'"\?%#$@\,\. \t\r\n]')

#SCHEMA = jsonschema(schema)

#These lists are the keys for python dictionaries
#these dictionaries will be written in csv files
NODE_FIELDS = ['id', 'lat', 'lon', 'user', 'uid', 'version', 'changeset', 'timestamp']
NODE_TAGS_FIELDS = ['id', 'key', 'value', 'type']
WAY_FIELDS = ['id', 'user', 'uid', 'version', 'changeset', 'timestamp']
WAY_TAGS_FIELDS = ['id', 'key', 'value', 'type']
WAY_NODES_FIELDS = ['id', 'node_id', 'position']
RELATION_FIELDS=['id', 'uid', 'changeset', 'timestamp', 'user', 'version']
RELATION_TAGS_FIELDS = ['id', 'key', 'value', 'type']
RELATION_MEMBERS_FIELDS=['id',  "ref_id", "ref_to", "role"]

#ALSO: validation functions from the exercises:
# ================================================== #
#               Helper Functions                     #
# ================================================== #

#This function takes in any element and matches it with our schema
#raises exception when errors are found
def validate_element(element, validator, schema=schema):
    """Raise ValidationError if element does not match schema"""
    if validator.validate(element, schema) is not True:
        print("Errors related to:")
        for case in validator.errors.items():
            print(case)
        #field, errors = case
        #print("field, errors", validator.errors.items())
        #message_string = "\nElement of type '{0}' has the following errors:\n{1}"
        #error_string = pprint.pformat(errors)
        
        raise Exception(message_string.format(field, error_string))

#Matches street type tags with the expected list and clean street names
def clean_street_names(key, street_name):
    #this is to change and clean street names
    expected = ["Street", "Avenue", "Boulevard", "Drive", "Court", "Place", "Square", "Lane", "Road", 
            "Trail", "Parkway", "Commons", "Way", "Loop", "Circle", "Highway", "Stars", "Plaza"]
    
    street_type_re = re.compile(r'\b\S+\.?$', re.IGNORECASE)
    
    mapping = { "St": "Street",
            "Rd": "Road",
            "Ave": "Avenue",
               "Dr": "Drive",
               "Ct": "Court",
               "Ln": "Lane",
               "Blvd": "Boulevard",
               "Trl": "Trail",
               "Pl": "Place",
               "Pkwy": "Parkway"
            }
    
    out_name=street_name
    if "street" in key:
        m = street_type_re.search(street_name, re.IGNORECASE)
        if m:
            street_type = m.group()
            #print(street_type)
            if street_type not in expected:
                for index, change in sorted(mapping.items()):
                    #print index, change, name
                    if index.casefold()==street_type.casefold() or index.casefold()+"."==street_type.casefold():
                        print("Original:", street_name)
                        out_name=re.sub(index, change, street_name, flags=re.IGNORECASE)
                        if out_name[-1]==".":
                            out_name=out_name[0:-1]
                        print("After change:", out_name)
                        break            
    return out_name
     
def clean_post_codes(postcodeval):
    real_code=postcodeval
    post = re.search(r'\d{5}', postcodeval)
    if post:
        real_code=post.group()
    else:
        print("strange post code: ", real_code)
    return real_code    

#Okay, we need shape element function - to write xml into python distionaries
#that we can then write up as csv
#need to slightly modify it for "relation":
#node_attr_fields=NODE_FIELDS, way_attr_fields=WAY_FIELDS, relation_attr_fields=RELATION_FIELDS,
def shape_element(element, problem_chars=PROBLEMCHARS, node_attr_fields=NODE_FIELDS, 
                  way_attr_fields=WAY_FIELDS, relation_attr_fields=RELATION_FIELDS, default_tag_type='regular'):
    """Clean and shape node/way/relation XML element to Python dict"""
    
    node_attribs = {}
    way_attribs = {}
    relation_attribs={}
    way_nodes = []
    relation_members=[]
    relation_nodes=[]
    tags = []  # Handle secondary tags the same way for both node, way and relation elements

    # YOUR CODE HERE
    if element.tag == 'node':
        for item in node_attr_fields:
            node_attribs[item]=element.attrib[item]
    
        #this v attribute of way tags is where we find the street names
        #so it should be changed here
        for subtag in element.iter("tag"):
            dicti={}
            #'id', 'key', 'value', 'type'
            dicti['id']=element.attrib['id']
            #print subtag
            key_holder=subtag.attrib['k']
            if ":" in key_holder:
                dicti['key']=key_holder.split(":",1)[1]
                dicti['type']=key_holder.split(":",1)[0]
            else:
                dicti['key']=key_holder
                dicti['type']="regular"
            poss_street=subtag.attrib['v']
            dicti['value']=clean_street_names(key_holder, poss_street)
            if "postcode" in key_holder:
                if "-" in poss_street:
                    dicti['value']=clean_post_codes(poss_street)
            tags.append(dicti)
            
        return {'node': node_attribs, 'node_tags': tags}

    elif element.tag == 'way':
        for item in way_attr_fields:
            way_attribs[item]=element.attrib[item]
    
        for subtag in element.iter("tag"):
            dicti={}
            #'id', 'key', 'value', 'type'
            dicti['id']=element.attrib['id']
            key_holder=subtag.attrib['k']
            if ":" in key_holder:
                dicti['key']=key_holder.split(":",1)[1]
                dicti['type']=key_holder.split(":",1)[0]
            else:
                dicti['key']=key_holder
                dicti['type']="regular"
            poss_street=subtag.attrib['v'] #again, check street names
            dicti['value']=clean_street_names(key_holder, poss_street)
            if "postcode" in key_holder:
                if "-" in poss_street:
                    dicti['value']=clean_post_codes(poss_street)
            tags.append(dicti)

        nd_posi=0
        for subtag in element.iter("nd"):
            dicti={}
            #'id', 'key', 'value', 'type'
            #print subtag
            dicti['id']=element.attrib['id']
            dicti["position"]=nd_posi
            dicti['node_id']=subtag.attrib['ref']
            nd_posi+=1
            way_nodes.append(dicti)
            
        return {'way': way_attribs, 'way_nodes': way_nodes, 'way_tags': tags}
    elif element.tag=="relation":
        for item in relation_attr_fields:
            relation_attribs[item]=element.attrib[item]
    
        for subtag in element.iter("tag"):
            dicti={}
            #'id', 'key', 'value', 'type'
            dicti['id']=element.attrib['id']
            key_holder=subtag.attrib['k']
            if ":" in key_holder:
                #print "addr", key_holder
                dicti['key']=key_holder.split(":",1)[1]
                dicti['type']=key_holder.split(":",1)[0]
            else:
                dicti['key']=key_holder
                dicti['type']="regular"
            poss_street=subtag.attrib['v'] #change street names
            dicti['value']=clean_street_names(key_holder, poss_street)
            if "postcode" in key_holder:
                if "-" in poss_street:
                    dicti['value']=clean_post_codes(poss_street)
            tags.append(dicti)

            #trouble trouble trouble
            for subtag in element.iter("member"):
                dicti={}
                #'id',  "ref_id", "ref_to", "role"
                #print subtag
                dicti['id']=element.attrib['id']
                dicti["ref_id"]=subtag.attrib['ref']
                dicti['ref_to']=subtag.attrib['type']
                dicti['role']=subtag.attrib['role']
                relation_members.append(dicti)
            
        return {'relation': relation_attribs, 'relation_members': relation_members, 'relation_tags': tags}

# ================================================== #
#               Main Function                        #
# ================================================== #
def process_map(file_in, folder_name, suffix, validate=True):
    """Iteratively process each XML element and write to csv(s)"""
    
    NODES_PATH = folder_name+"nodes"+suffix
    NODE_TAGS_PATH = folder_name+"nodes_tags"+suffix
    WAYS_PATH = folder_name+"ways"+suffix
    WAY_NODES_PATH = folder_name+"ways_nodes"+suffix
    WAY_TAGS_PATH = folder_name+"ways_tags"+suffix
    RELATION_PATH = folder_name+"relations"+suffix
    RELATION_MEMBERS_PATH = folder_name+"relations_members"+suffix
    RELATION_TAGS_PATH = folder_name+"relations_tags"+suffix
    

    with codecs.open(NODES_PATH, 'w') as nodes_file, \
         codecs.open(NODE_TAGS_PATH, 'w') as nodes_tags_file, \
         codecs.open(WAYS_PATH, 'w') as ways_file, \
         codecs.open(WAY_NODES_PATH, 'w') as way_nodes_file, \
         codecs.open(WAY_TAGS_PATH, 'w') as way_tags_file, \
         codecs.open(RELATION_PATH, 'w') as relation_file, \
         codecs.open(RELATION_MEMBERS_PATH, 'w') as relation_members_file, \
         codecs.open(RELATION_TAGS_PATH, 'w') as relation_tags_file:
                
                
        nodes_writer = csv.DictWriter(nodes_file, fieldnames=NODE_FIELDS)
        node_tags_writer = csv.DictWriter(nodes_tags_file, fieldnames=NODE_TAGS_FIELDS)
        ways_writer = csv.DictWriter(ways_file, fieldnames=WAY_FIELDS)
        way_nodes_writer = csv.DictWriter(way_nodes_file, fieldnames=WAY_NODES_FIELDS)
        way_tags_writer = csv.DictWriter(way_tags_file, fieldnames=WAY_TAGS_FIELDS)
        relation_writer = csv.DictWriter(relation_file, fieldnames=RELATION_FIELDS)
        relation_members_writer = csv.DictWriter(relation_members_file, fieldnames=RELATION_MEMBERS_FIELDS)
        relation_tags_writer = csv.DictWriter(relation_tags_file, fieldnames=RELATION_TAGS_FIELDS)
        
        nodes_writer.writeheader()
        node_tags_writer.writeheader()
        ways_writer.writeheader()
        way_nodes_writer.writeheader()
        way_tags_writer.writeheader()
        relation_writer.writeheader()
        relation_members_writer.writeheader()
        relation_tags_writer.writeheader()
        
        validator = cerberus.Validator()

        for element in get_element(file_in, tags=('node', 'way', 'relation')):
            el = shape_element(element)
            if el:
                if validate is True:
                    validate_element(el, validator)

                if element.tag == 'node':
                    nodes_writer.writerow(el['node'])
                    node_tags_writer.writerows(el['node_tags'])
                elif element.tag == 'way':
                    ways_writer.writerow(el['way'])
                    way_nodes_writer.writerows(el['way_nodes'])
                    way_tags_writer.writerows(el['way_tags'])
                elif element.tag == 'relation':
                    relation_writer.writerow(el['relation'])
                    relation_members_writer.writerows(el['relation_members'])
                    relation_tags_writer.writerows(el['relation_tags'])


