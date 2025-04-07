from PIL import Image

# PNG'yi ICO'ya çevir
img = Image.open('tadu.png')
icon_sizes = [(16,16), (32,32), (48,48), (64,64), (128,128), (256,256)]
img.save('tadu.ico', format='ICO', sizes=icon_sizes) 