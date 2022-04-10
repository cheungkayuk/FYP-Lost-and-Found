import os, os.path, shutil

folder_path = ".\downloaded_images\All"

images = sorted(os.listdir(folder_path))

print(len(images))
input()

split_length = 15000

first10000 = images[:split_length]

after10000 = images[split_length:]

print(len(first10000), len(after10000))
input()

for image in first10000:
    folder_name = "first10000"

    new_path = os.path.join(folder_path, folder_name)
    if not os.path.exists(new_path):
        os.makedirs(new_path)

    old_image_path = os.path.join(folder_path, image)
    new_image_path = os.path.join(new_path, image)
    shutil.move(old_image_path, new_image_path)
    
for image in after10000:
    folder_name = "after10000"

    new_path = os.path.join(folder_path, folder_name)
    if not os.path.exists(new_path):
        os.makedirs(new_path)

    old_image_path = os.path.join(folder_path, image)
    new_image_path = os.path.join(new_path, image)
    shutil.move(old_image_path, new_image_path)

