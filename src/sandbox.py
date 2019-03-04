import encoder
import os

from settings import *

i = 0
while i < 10:
    print(os.path.join(DATA_DIR, (str(i).zfill(3) + "_" + DATA_FILENAME)))
    i = i + 1
