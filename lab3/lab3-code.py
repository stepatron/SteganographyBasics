from PIL import Image
import math

img_in = img_out = 0
img_plain_path = r'C:\Users\stepa\Documents\ИТМО\Основы стеганографии\Лаба 3\img_plain.bmp'
img_encode_path = r'C:\Users\stepa\Documents\ИТМО\Основы стеганографии\Лаба 3\img_encode.bmp'
block_size = 8

# Проверка результата выполнения функции
def check_result(res, msg):
    if res == -1:
        print(msg)
        exit1()

# Завершеине работы при ошибке
def exit1():
    if img_in != 0:
        img_in.close()
    if img_out != 0:
        img_out.close()
    print('exit(-1)')
    exit(-1)

# Проверка возможности встраивания
def can_encode(msg_plain, block_size, img_plain_path):
    img, img_res = getPixels(img_plain_path)
    if len(msg_plain)*7+7 > (img_res[0]*img_res[1]/(block_size**2))*26:
        return -1
    return 0

# Создание списка пикселей
def getPixels(img_path):
    img = Image.open(img_path)
    img_res = img.size
    pixels = list(img.getdata())
    img.close()
    return pixels, img_res

# Создание изображения
def putPixels(img_path, pixels, img_res):
    img = Image.new('RGB', img_res)
    img.putdata(pixels)
    img.save(img_path)
    img.close()
    return 0

# Кодирование двоичной строки
def strEncode(msg_plain):
    msg_cypher = ''
    for pix_num in msg_plain:
        if pix_num == ' ':
            msg_cypher += '1111111'
        else:
            msg_cypher += format(ord(pix_num)-1024, '07b')
    msg_cypher += '0000000'
    return msg_cypher

# Декодирование двоичной строки
def strDecode(msg_cypher):
    str_temp = ''
    plain_word = ''
    for bit in range(len(msg_cypher)):
        str_temp += msg_cypher[bit]
        if len(str_temp) == 7:
            if str_temp == '1111111':
                plain_word += ' '
            else:
                plain_word += chr(int(str_temp, 2)+1024)
            str_temp = ''
    return plain_word

# Создание списков квадратных блоков их списка RGB пикселей
def tupleToBlocks(pixels, img_res, block_size):
    blocks_r = []
    blocks_g = []
    blocks_b = []
    color_id = 0
    block_temp = []
    for blocks_list in [blocks_r, blocks_g, blocks_b]:
        for column_num in range(0, img_res[0], block_size):
            for row_num in range(0, img_res[0]*img_res[1], img_res[0]):
                row_temp = []
                for pix_num in range(block_size):
                    row_temp.append(
                        pixels[column_num+row_num+pix_num][color_id])
                block_temp.append(row_temp)
                if len(block_temp) == block_size:
                    blocks_list.append(block_temp)
                    block_temp = []
        color_id += 1
    return blocks_b+blocks_g+blocks_r

# Создание списка RGB пикселей из списков квадратных блоков
def blocksToTuple(blocks, img_res, block_size):
    pixels = []
    blocks_b = blocks[0:int(len(blocks)/3)]
    blocks_g = blocks[int(len(blocks)/3):int(len(blocks)/3)*2]
    blocks_r = blocks[int(len(blocks)/3)*2:int(len(blocks))]
    pix_c = 0
    for column_num in range(int(img_res[1]/block_size)):
        for row_num in range(block_size):
            for block_num in range(0, len(blocks_r), int(img_res[1]/block_size)):
                for pix_num in range(block_size):
                    pix_c += 1
                    row_temp = (blocks_r[column_num+block_num][row_num][pix_num], blocks_g[column_num + block_num][row_num][pix_num], blocks_b[column_num+block_num][row_num][pix_num])
                    pixels.append(row_temp)
    pixels = tuple(pixels)
    return pixels

# Дискретно косинусное преобразование(ДКП)
def enDCT(block_plain):
    block_enDCTed = []
    for k in range(len(block_plain)):
        row_temp = []
        for l in range(len(block_plain)):
            block_sum = 0
            for m in range(len(block_plain)):
                for n in range(len(block_plain)):
                    block_sum += block_plain[m][n] * math.cos(math.pi*k*((2*m+1)/(2*len(block_plain)))) * math.cos(math.pi*l*((2*n+1)/(2*len(block_plain))))
            if k == 0 and l == 0:
                alpha = 1
            elif k == 0 or l == 0:
                alpha = math.sqrt(2)
            else:
                alpha = 2
            block_sum = (alpha*block_sum)/len(block_plain)
            row_temp.append(block_sum)
        block_enDCTed.append(row_temp)
    return block_enDCTed

# Обратное ДКП
def deDCT(block_enDCTed):
    block_deDCTed = []
    for m in range(len(block_enDCTed)):
        row_temp = []
        for n in range(len(block_enDCTed)):
            block_sum = 0
            for k in range(len(block_enDCTed)):
                for l in range(len(block_enDCTed)):
                    if k == 0 and l == 0:
                        alpha = 1
                    elif k == 0 or l == 0:
                        alpha = math.sqrt(2)
                    else:
                        alpha = 2
                    block_sum += (alpha/len(block_enDCTed)) * block_enDCTed[k][l] * math.cos(math.pi*k*((2*m+1)/(2*len(block_enDCTed)))) * math.cos(math.pi*l*((2*n+1)/(2*len(block_enDCTed))))
            row_temp.append(round(block_sum))
        block_deDCTed.append(row_temp)
    return block_deDCTed

# Рассчет параметра PSNR
def psnr(img_path_1, img_path_2):
    img_a = getPixels(img_path_1)[0]
    img_b = getPixels(img_path_2)[0]
    mse_r = mse_g = mse_b = mse_t = psnr = 0
    for y in range(len(img_a)):
        for x in range(3):
            if x == 0:
                mse_r += (int(img_b[y][x])-int(img_a[y][x]))**2
            elif x == 1:
                mse_g += (int(img_b[y][x])-int(img_a[y][x]))**2
            elif x == 2:
                mse_b += (int(img_b[y][x])-int(img_a[y][x]))**2
    mse_t = (mse_r+mse_g+mse_b)/(3*len(img_a))
    rmse = round(math.sqrt(mse_t), 3)
    psnr = round(10*math.log10((255**2)/mse_t), 3)
    return psnr, rmse

# Встраивание сообщения в коэффициенты ДКП
def encode(msg_plain, block_size, img_plain_path, img_encode_path):
    # Кодирование двоичной строки
    msg_cypher = strEncode(msg_plain)
    # Создание списка пикселей
    pixels, img_res = getPixels(img_plain_path)
    # Получение списков квадратных блоков
    blocks_plain = tupleToBlocks(pixels, img_res, block_size)
    # ДКП блоков
    blocks_enDCTed = []
    [blocks_enDCTed.append(enDCT(block)) for block in blocks_plain]
    # Встраивание
    block_row = [0,0,1,1,2,2,3,3,4,4,5,5,6,6,7,7]
    block_elem = [7,6,7,6,5,4,5,4,3,2,3,2,1,0,1,0]
    bit_num = 0
    for block_num in range(len(blocks_enDCTed)):
        for adr in range(16):
            if bit_num == len(msg_cypher):
                break
            if msg_cypher[bit_num] == '0':
                if round(blocks_enDCTed[block_num][block_row[adr]][block_elem[adr]]) % 2 == 1:
                    blocks_enDCTed[block_num][block_row[adr]][block_elem[adr]] -= 1
            elif msg_cypher[bit_num] == '1':
                if round(blocks_enDCTed[block_num][block_row[adr]][block_elem[adr]]) % 2 == 0:
                    blocks_enDCTed[block_num][block_row[adr]][block_elem[adr]] += 1
            bit_num += 1
    # Обратное ДКП
    blocks_deDCTed = []
    [blocks_deDCTed.append(deDCT(block)) for block in blocks_enDCTed]
    # Создание изображения
    pixels = blocksToTuple(blocks_deDCTed, img_res, block_size)
    putPixels(img_encode_path, pixels, img_res)
    return 0

# Извлечение сообщения из коэффициентов ДКП
def decode(img_encode_path, block_size):
    # Создание списка пикселей
    pixels, img_res = getPixels(img_encode_path)
    # Получение списков квадратных блоков
    blocks_encode = tupleToBlocks(pixels, img_res, block_size)
    # ДКП блоков
    blocks_enDCTed = []
    [blocks_enDCTed.append(enDCT(block)) for block in blocks_encode]
    # Извлечение двоичной строки
    msg_cypher = ''
    bit_count = zero_count = 0
    block_row = [0,0,1,1,2,2,3,3,4,4,5,5,6,6,7,7]
    block_elem = [7,6,7,6,5,4,5,4,3,2,3,2,1,0,1,0]
    for block_num in range(len(blocks_enDCTed)):
        for adr in range(16):
            if round(blocks_enDCTed[block_num][block_row[adr]][block_elem[adr]]) % 2 == 0:
                msg_cypher += '0'
                zero_count += 1
                bit_count += 1
            if round(blocks_enDCTed[block_num][block_row[adr]][block_elem[adr]]) % 2 == 1:
                msg_cypher += '1'
                bit_count += 1
            if bit_count == 7 and zero_count != 7:
                bit_count = 0
                zero_count = 0
            elif bit_count == 7 and zero_count == 7:
                msg_cypher = msg_cypher[:-7]
                break
    # Декодирование двоичной строки
    plain_word = strDecode(msg_cypher)
    return plain_word


# ---------------------------------------------------------------------------------------------------
# Выбор встраивания/извлечения
option = input('Для встраивания введите 1, для извлечения введите 2: ')
if option not in '12':
    print('Неверный символ: ', option)
    exit1()
# Встраивание
if option == '1':
    # Ввод сообщения
    msg_plain = input('Введите сообщение для встраивания в текст: ')
    # Проверка возможности встраивания
    res = can_encode(msg_plain, block_size, img_plain_path)
    check_result(res, 'Нехватка блоков для встраивания')
    # Встраивание сообщения в коэффициенты ДКП
    res = encode(msg_plain, block_size, img_plain_path, img_encode_path)
    check_result(res, 'Не удалось выполнить встраивание')
    # Рассчет параметра PSNR
    psnrrmse = psnr(img_plain_path, img_encode_path)
    print('Встроено сообщение \"', msg_plain,
          '\" в изображение \"', img_encode_path, '\"', sep='')
    print('Параметр RMSE равен', psnrrmse[1])
    print('Параметр PSNR равен', psnrrmse[0], 'dB')
# Извлечение
elif option == '2':
    # Извлечение сообщения из коэффициентов ДКП
    res = decode(img_encode_path, block_size)
    check_result(res, 'Не удалось выполнить извлечение')
    print('Извлечено сообщение \"', res[:13],
          '\" из изображения \"', img_encode_path, '\"', sep='')
exit(0)
# ----------------------------------------------------------------------------------------------------