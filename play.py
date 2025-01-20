# read IMG_0308.JPG and print captured time
from PIL import Image
from PIL.ExifTags import TAGS

def get_image_capture_time(image_path):
  with Image.open(image_path) as img:
    exif_data = img._getexif()
    if exif_data is not None:
      for tag_id, value in exif_data.items():
        tag = TAGS.get(tag_id, tag_id)
        if tag == 'DateTimeOriginal':
          return value
    return None

capture_time = get_image_capture_time('IMG_0308.JPG')
print("Captured time:", capture_time)
