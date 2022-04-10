import os
import shutil

main_folder = 'downloaded_images_val/downloaded_images'

allClasses = []
for item in os.listdir(main_folder):
    if item == 'allClasses':
        continue
    classFiles = [os.path.splitext(filename)[0]
                  for filename in os.listdir(main_folder + '/' + item)]
    
    allClasses.append([item, list(set(classFiles))])

seen = set()
dupes = []
uniq = []

for item in allClasses:
    for x in item[1]:
        if x in seen:
            dupes.append((item[0], x))
        else:
            uniq.append((item[0], x))
            seen.add(x)

dupes = list(set(dupes))
print(len(dupes))

allClassesFolder = main_folder + '/allClasses'
if not os.path.exists(allClassesFolder):
    os.makedirs(allClassesFolder)

for unique in uniq:
    item_folder = main_folder + '/' + unique[0]
    filename = unique[1]
    src = item_folder + '/' + filename
    dst = main_folder + '/allClasses/' + filename
    shutil.copyfile(src+'.jpg', dst+'.jpg')
    shutil.copyfile(src+'.txt', dst+'.txt')

for duplicate in dupes:
    item_folder = main_folder + '/' + duplicate[0]
    filename = duplicate[1]+'.txt'
    dstfile = main_folder + '/allClasses/' + filename
    sourcefile = item_folder + '/' + filename

    with open(sourcefile) as f_src:
        contents = f_src.read()
        
    with open(dstfile, "a+") as f_dst:
        f_dst.seek(0)
        data = f_dst.read(100)
        if len(data) > 0 :
            f_dst.write("\n")
        f_dst.write(contents)
    
