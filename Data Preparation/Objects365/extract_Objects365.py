import json
import cv2


# json_file = "Objects365\Train\zhiyuan_objv2_train.json"
# MemoryError

# json filename
json_file = "Objects365\Val\zhiyuan_objv2_val.json"

# open the json file
f = open(json_file)

# load the json file
data = json.load(f)

# target class list for filtering
classlist = ['Handbag/Satchel', 'Backpack', 'Cell Phone', 'Luggage', 'Wallet/Purse']

# classlist = ['Telephone']

# get the class id of the target classes
classlist_ids = []
for category in data["categories"]:
    if category['name'] in classlist:
        print(category)
        classlist_ids.append(category['id'])

# the name of json file to be created
image_annotation_json = 'image_annotation.json'

# extract the filtered annotations from the loaded json
image_ann_id = {}
for annotation in data['annotations']:
    if annotation['category_id'] in classlist_ids:
        for image in data['images']:
            if annotation['image_id'] == image['id']:
                if image_ann_id.get(image['id']) is not None:
                    image_ann_id[image['id']]['annotations'].append(annotation)
                else:
                    image_ann_id[image['id']] = image
                    image_ann_id[image['id']]['annotations'] = [annotation]

                print("Extracting")

# Serializing json 
# json_object = json.dumps(image_ann_id, indent = 4)

# Write to json
with open(image_annotation_json, "w") as outfile:
    # outfile.write(json_object)
    json.dump(image_ann_id, outfile)


f.close()

print("Finsihed")
