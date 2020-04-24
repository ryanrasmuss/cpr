import json
import csv

with open('output.txt') as f:
    data = json.load(f)
    #print(data)

    #print()

    objects = data['objects']

    #print (objects)

    with open("deletehosts.csv", 'w', newline='') as outfile:
        writer = csv.writer(outfile)
        # header needs to be written
        writer.writerow(["name"])

        for obj in objects:
            if("tags" in obj) and bool(obj["tags"]):
                tag_section = obj["tags"]
                for tag in tag_section:
                    tag_name = tag["name"]
                    if "demo" == tag_name:
                        writer.writerow([obj["name"]])

    outfile.close()

    print("Found demo objects")


'''
    with open("hosts.csv", 'w', newline='') as outfile:
        writer = csv.writer(outfile)
        # header needs to be written
        writer.writerow(["name", "ip-address"])

        for obj in objects:
            #print(obj)
            # parse what we want
            name = obj['name']
            ip = obj['ipv4-address']
            # write it to csv
            writer.writerow([name, ip])
'''

'''
    for obj in objects:
        print ()
        if ("tags" in obj) and bool(obj["tags"]):
            tag_section = obj["tags"]
            print(tag_section)
            print()
            for tag in tag_section:
                print(tag["name"])
                if "esxi" == tag["name"]:
                    print("We have an esxi tag!")


        print()
'''