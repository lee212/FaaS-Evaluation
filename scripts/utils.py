import json

def to_file(fname, data):    
    with open(fname, "w") as f: 
        try:
            json.dump(data, f, indent=4)
        # TypeError: <botocore.response.StreamingBody object at 0x7f38b8fecc18>
        # is not JSON serializable
        except TypeError:
            for d in data:
                del(d['Payload'])
            json.dump(data, f, indent=4)


