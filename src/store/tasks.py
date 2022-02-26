from PIL import Image
def imageResize(imagepath):
    try:
        image = Image.open(imagepath, 'r')
        image_size = image.size
        old_image_width = image_size[0]
        old_image_height = image_size[1]
        old_image_ratio = float(round(old_image_width/old_image_height, 4))
        new_width = 1000
        new_height = 1358
        background_image = Image.new('RGB', (new_width, new_height), (255, 255, 255))

        if old_image_ratio >= 1:
            temp_new_height = int(new_width/old_image_ratio)
            new_image = image.resize((new_width,temp_new_height))
            background_image.paste(new_image,(0,(new_height-temp_new_height)//2))
            
        elif old_image_ratio < 1 and old_image_ratio > 0:
            temp_new_width = int(old_image_ratio*new_height)
            new_image = image.resize((temp_new_width,new_height))
            background_image.paste(new_image, ((new_width-temp_new_width)//2, 0))
        print('image resize success----',background_image.size)
        background_image.save(imagepath)
        return True
    except Exception as ex:
        print('could not change image ratio-----',ex)
        try:
            image.save(imagepath)
            return False
        except Exception as ex:
            print(ex)
            return False

if __name__ == "__main__":
    imageResize('media/product_image/samsung_note_10.jpg')