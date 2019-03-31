import pygame as pg
import numpy as np
import PIL.ImageOps

from keras.models import load_model
from PIL import Image

class GameTools:
    def roundline(srf, color, start, end, radius=5):
            dx = end[0]-start[0]
            dy = end[1]-start[1]
            distance = max(abs(dx), abs(dy))
            for i in range(distance):
                x = int( start[0]+float(i)/distance*dx)
                y = int( start[1]+float(i)/distance*dy)
                pg.draw.circle(srf, color, (x, y), radius)

    def predict(srf):
        # Load the model that was already pre-trained
        model = load_model("src/static/file/mnistModel.h5")
        # First, format the image in a bitstring for pillow
        pil_string = pg.image.tostring(srf, "RGB", False)
        # Create the PIL Image object from the RGBA bitstring above
        drawing = Image.frombytes("RGB", (400,400), pil_string)
        # Invert the drawing, since the MNIST data set is white images on black
        drawing = PIL.ImageOps.invert(drawing)
        # Resize the Image to 28x28 from 400x400, removing alpha and RGB channels
        wpercent = (28/float(drawing.size[0]))
        hsize = int((float(drawing.size[1])*float(wpercent)))
        drawing = drawing.resize((28, hsize), Image.ANTIALIAS).convert("L")
        drawing.show()
        # Convert the drawing to a numpy array for the model, with shape 1,28,28,1
        drawing_arr = np.array(drawing).reshape(1,28,28,1)
        # Make the prediction on the loaded model
        predictions = model.predict(drawing_arr)
        # TODO: Something with the results
        print(np.argmax(predictions[0]))
