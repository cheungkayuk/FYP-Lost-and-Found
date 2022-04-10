import json
import os
import shutil


json_file = "image_annotation_all.json"

colour = (255, 0, 0)
thickness = 1

f = open(json_file)

data = json.load(f)

allPatches = 'AllPatches'

if not os.path.exists(allPatches):
    os.makedirs(allPatches)

for image_id in data:
    image = data.get(image_id)
    if(image['file_name']):
        path_list = image['file_name'].split('/')
        patch = path_list[-2]
        imagename = path_list[-1]
        filename_without_ext = (patch + '/' + imagename).split('.')[0]
        filename = filename_without_ext + '.txt'
        s = ""
        anns = image["annotations"]
        for i in range(len(anns)):
            # start_point = (bbox[0], bbox[1])
            # end_point = (bbox[0]+bbox[2], bbox[1]+bbox[3])
            category_id = anns[i]["category_id"]
            topLeftX = anns[i]['bbox'][0] / image['width']
            topLeftY = anns[i]['bbox'][1] / image['height']
            width = anns[i]['bbox'][2] / image['width']
            height = anns[i]['bbox'][3] / image['height']
            
            s += str(category_id) + " " + str((topLeftX + (topLeftX + width)) / 2) + " " + \
            str((topLeftY + (topLeftY + height)) / 2) + " " + \
            str(width) + " " + \
            str(height)
            
            if(i < len(anns) - 1):
                s += '\n'

        with open(filename, 'w') as label_handler:
            label_handler.write(s)


        dst = (allPatches + '/' + imagename).split('.')[0]
        shutil.copyfile(patch + '/' + imagename, dst+'.jpg')
        shutil.move(filename, dst + '.txt')

f.close()
