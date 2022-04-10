from pycocotools.coco import COCO # pip install pycocotools
import requests
import os
import sys
import threading

def makeDirectory(dirName):
    try:
        os.mkdir(dirName)
        print(f"\nMade {dirName} Directory.\n")
    except:
        pass

def getImagesFromClassName(className, classIndex):
    makeDirectory(f'downloaded_images/{className}')
    catIds = coco.getCatIds(catNms=[className])
    imgIds = coco.getImgIds(catIds=catIds )
    images = coco.loadImgs(imgIds)

    print(f"Total Images: {len(images)} for class '{className}'")

    for im in images:
        image_file_name = im['file_name']
        label_file_name = im['file_name'].split('.')[0] + '.txt'

        fileExists = os.path.exists(f'downloaded_images/{className}/{image_file_name}')
        if(not fileExists):
            img_data = requests.get(im['coco_url']).content
            annIds = coco.getAnnIds(imgIds=im['id'], catIds=catIds, iscrowd=None)
            anns = coco.loadAnns(annIds)    
            print(f"{className}. Downloading - {image_file_name}")
            s = ""
            for i in range(len(anns)):
                # Yolo Format: center-x center-y width height
                # All values are relative to the image.
                topLeftX = anns[i]['bbox'][0] / im['width']
                topLeftY = anns[i]['bbox'][1] / im['height']
                width = anns[i]['bbox'][2] / im['width']
                height = anns[i]['bbox'][3] / im['height']
                
                s += str(classIndex) + " " + str((topLeftX + (topLeftX + width)) / 2) + " " + \
                str((topLeftY + (topLeftY + height)) / 2) + " " + \
                str(width) + " " + \
                str(height)
                
                if(i < len(anns) - 1):
                    s += '\n'
            
            with open(f'downloaded_images/{className}/{image_file_name}', 'wb') as image_handler:
                image_handler.write(img_data)
            with open(f'downloaded_images/{className}/{label_file_name}', 'w') as label_handler:
                label_handler.write(s)
        else:
           print(f"{className}. {image_file_name} - Already Downloaded.")

argumentList = sys.argv

classes = argumentList[1:]

classes = [class_name.lower() for class_name in classes] # Converting to lower case


if(classes[0] == "--help"):
    with open('classes.txt', 'r') as fp:
        lines = fp.readlines()
    print("**** Classes ****\n")
    [print(x.split('\n')[0]) for x in lines]
    exit(0)     

print("\nClasses to download: ", classes, end = "\n\n")

makeDirectory('downloaded_images')

coco = COCO('instances_val2017.json')
cats = coco.loadCats(coco.getCatIds())
nms=[cat['name'] for cat in cats]

for name in classes:
    if(name not in nms):
        print(f"{name} is not a valid class, Skipping.")
        classes.remove(name)

threads = []

# Creating threads for every class provided.
for i in range(len(classes)):
    t = threading.Thread(target=getImagesFromClassName, args=(classes[i], i+1, )) 
    threads.append(t)
    
for t in threads:
    t.start()

for t in threads:
    t.join()

print("Done.")
