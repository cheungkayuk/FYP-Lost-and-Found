import json
import os
import cv2


json_file = "image_annotation_Telephone.json"

patchFolder = 'patch0'

colour = (255, 0, 0)
thickness = 1

f = open(json_file)

data = json.load(f)

for image_id in data:
    image = data.get(image_id)
    if(image['file_name']):
        path_list = image['file_name'].split('/')
        patch = path_list[-2]
        if patch == patchFolder:
            imagename = path_list[-1]
            img = cv2.imread(patch + '/' + imagename)
            for annotation in image["annotations"]:
                bbox = annotation['bbox']
                bbox = [int(x) for x in bbox]
                start_point = (bbox[0], bbox[1])
                end_point = (bbox[0]+bbox[2], bbox[1]+bbox[3])
                img = cv2.rectangle(img, start_point, end_point,
                                     colour, thickness)
            cv2.imwrite(imagename, img)
            input()

f.close()
