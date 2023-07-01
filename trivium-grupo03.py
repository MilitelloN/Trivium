import numpy as np
from PIL import Image
import matplotlib.pyplot as plt
import hashlib
import sys


def showPicture(image):
    plt.imshow(image)
    plt.show()

def getBitsFrom(key):
    bits = ''.join(format(ord(caracter), '08b') for caracter in key)
    return bits.zfill(80) if len(bits) < 80 else bits[:80]

def trivium(key,iv,keystreamSize):
    keyBits = getBitsFrom(key)
    ivBits = getBitsFrom(iv)

    # 80 keyBits + 13 0's + 80 ivbits + 4 0's + 108 0's + 3 1's = 288
    stateS = keyBits + "0"*13 + ivBits + "0"*112 + "1"*3
    
    state = []
    for bit in stateS:
        state.append(int(bit,2))
    
    for round in range (0,4 * 288):
        t1 = state[65] ^ state[90] & state[91] ^ state[92] ^ state[170]
        t2 = state[161] ^ state[174] & state[175] ^ state[176]  ^ state[263]
        t3 = state[242] ^ state[285] & state[286] ^ state[287]^ state[68]

        state.pop()
        state.insert(0,0)

        state[0] = t3
        state[93] = t1
        state[177] = t2

    keyStream = ""
    round = 0
    while(round < keystreamSize):
        t1 = state[65] ^ state[92]         
        t2 = state[161] ^ state[176]
        t3 = state[242] ^ state[287]

        keyStream += str(t1 ^ t2 ^ t3)
        
        t1 = t1 ^ state[90] & state[91] ^ state[170]
        t2 = t2 ^ state[174] & state[175] ^ state[263]
        t3 = t3 ^ state[285] & state[286] ^ state[68]         
        
        state.pop()
        state.insert(0,0)

        state[0] = t3
        state[93] = t1
        state[177] = t2
        round += 1
    
    return keyStream

def img2MatPixel(image):
    return np.array(image)

def matPixel2Img(mat):
    return Image.fromarray(mat)

def getHash(img):
    imgMat = img2MatPixel(img)
    hash_ = hashlib.sha256()
    hash_.update(img2MatPixel(imgMat))
    return hash_.hexdigest()

# Convierte la imagen a matriz, cifra y vuelve a convertir la matriz a imagen.
def des_cifrado(image,keyStream):
    matImage = img2MatPixel(image)

    matC = matImage.flatten()
    keyInt = int(keyStream,2)
    
    for pixel in range(0,len(matC)):
        matC[pixel] = np.bitwise_xor(matC[pixel], keyInt)

    matImage = matC.reshape(matImage.shape)

    return matPixel2Img(matImage)



# ---------------- INICIO MAIN ----------------------
# Config de las imagenes
nombre = sys.argv[2]
imgOriginalNombre = "img/" + nombre + ".png"
imgCifradaNombre = "img/" + nombre + "Cifrada.png"
imgDescifradaNombre = "img/" + nombre + "Descifrada.png"

# Abro imagen
nombreImg = imgOriginalNombre if sys.argv[1] == "C" or sys.argv[1] == "c" else imgCifradaNombre
img = Image.open(nombreImg).convert('RGB')
print(f"{nombreImg}: {getHash(img)}")

# Genero la clave
keyStream = trivium(sys.argv[3],"M473m471C4_4pl1c4D4",40)
#print(f"Keystream: {keyStream}")

# (Des)cifro la imagen
imagenResultado = des_cifrado(img,keyStream)
nombreResultado = imgCifradaNombre if sys.argv[1] == "C" or sys.argv[1] == "c" else imgDescifradaNombre
imagenResultado.save(nombreResultado)
print(f"{nombreResultado}: {getHash(imagenResultado)}")


print("Fin de la operacion")



'''
    Proceso De cifrado:
    
    1) Abro la imagen y la convierto a una matriz de pixeles
    3) Genero el keystream con una clave alfanumerica y un iv.
    4) Cifro cada pixel de la matriz con el keystream
    5) Esta matriz cifrada la convierto a una imagen
    6) Muestro la imagen cifrada
'''