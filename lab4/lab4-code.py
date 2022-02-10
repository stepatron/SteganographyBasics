import math
import random
import numpy as np
import cv2

plain_path = r'C:\Users\stepa\Documents\ИТМО\Основы стеганографии\Лаба 4\plain.avi'
encode_path = r'C:\Users\stepa\Documents\ИТМО\Основы стеганографии\Лаба 4\encode.avi'
pos_percent = 0.5 # процент числа позиций (от 0.01 до 1)
h_percent = 0.1 # процент высоты рамки для встраивания (от 0.01 до 0.5)
w_percent = 0.1 # процент ширины рамки для встраивания (от 0.01 до 0.5)

# Кодирование двоичной строки
def strEncode(msg_plain):
    msg_cypher = ''
    for m in msg_plain:
        if m == ' ': 
            msg_cypher += '1111111'
        else: 
            msg_cypher += format(ord(m)-1024, '07b')
    msg_cypher += '0000000'
    return msg_cypher

# Декодирование двоичной строки
def strDecode(msg_cypher):
    temp = ''
    msg_plain = ''
    for b in range(len(msg_cypher)):
        temp += msg_cypher[b]
        if len(temp) == 7:
            if temp == '1111111': 
                msg_plain += ' '
            elif temp == '0000000':
                break
            else: 
                msg_plain += chr(int(temp, 2)+1024)
            temp = ''
    return msg_plain

# Преобразование видео-контейнера в список BGR кадров
def videoToList(path):
    frames_list = []
    # Открываем видео-контейнер на чтение
    vid_in = cv2.VideoCapture(path)
    # Считываем первый кадр
    is_frame, frame = vid_in.read()
    vid_height, vid_width = frame.shape[:2]
    vid_size = (vid_width, vid_height)
    # Считываем последующие кадры
    while is_frame:
        frames_list.append(frame)
        is_frame, frame = vid_in.read()
    vid_in.release()
    return tuple(frames_list), vid_size

# Преобразование списка BGR кадров в видео-контейнер
def listToVideo(frames_list, vid_size, path):
    # Создаем видео-контейнер на запись с кодеком и фпс
    video_out = cv2.VideoWriter(path, cv2.VideoWriter_fourcc(*'FFV1'), 25, vid_size)
    # Записываем все кадры
    for i in range(len(frames_list)):
        video_out.write(frames_list[i])
    video_out.release()
    return 0

def canEmbed(msg_cypher, vid_size, frames_count):
    pre_size = len(bin(frames_count)) - 2
    vid_width, vid_height = vid_size
    pos_width = math.ceil(vid_width*w_percent)
    pos_height = math.ceil(vid_height*h_percent)
    pos_count = math.ceil(((vid_width*pos_height)*2 + ((vid_height-2*pos_height)*pos_width)*2)*pos_percent) 
    bit_count = math.ceil(len(msg_cypher) / (pos_count - pre_size*2)) * pos_count
    pos_count *= frames_count
    if bit_count > pos_count:
        print('Недостаточно кадров для встраивания')
        exit(-1)

# Генерация списока позиций в кадре для встраивания
def getPositions(vid_size):
    pos_list = []
    pos_list_final = []
    vid_width, vid_height = vid_size
    pos_width = math.ceil(vid_width*w_percent)
    pos_height = math.ceil(vid_height*h_percent)
    # Генерируем список позиций для встраивания
    [ [ pos_list.append(tuple((a, b))) for b in range(vid_width) ] for a in range(vid_height-pos_height, vid_height) ] #нижняя рамка
    [ [ pos_list.append(tuple((a, b))) for b in range(vid_width-pos_width, vid_width) ] for a in range(pos_height, vid_height-pos_height) ] #правая рамка
    [ [ pos_list.append(tuple((a, b))) for b in range(pos_width) ] for a in range(pos_height, vid_height-pos_height) ] #левая рамка
    [ [ pos_list.append(tuple((a, b))) for b in range(vid_width) ] for a in range(pos_height) ] #верхняя рамка
    random.seed(3) #Ключ для случайного перемешивания
    # Перемешивание списка позиций
    random.shuffle(pos_list)
    # Выборка позиций для встраивания в кадр 
    for i in range(0, len(pos_list), round(1/pos_percent)):
        pos_list_final.append(pos_list[i])
    return tuple(pos_list_final)

# Разбиение двоичной строки на список строк формата (№ блока + содержимое + № блока)
def msgToList(msg_cypher, list_size, frames_count):
    msg_cypher_list = []
    pre_size = len(bin(frames_count)) - 2
    n = 0
    for i in range(0, len(msg_cypher), list_size-pre_size*2):
        # При несовпадении длин остатка сообщения и блока добавление '0'ей в конец сообщения
        if len(msg_cypher[i:i+list_size-pre_size*2]) < list_size-pre_size*2:
            msg_cypher_list.append(format(n, '0'+str(pre_size)+'b') + msg_cypher[i:i+list_size-pre_size*2] + (list_size-pre_size*2 - len(msg_cypher[i:i+list_size-pre_size*2]))*'0' + format(n, '0'+str(pre_size)+'b'))
        # Добавление номера блока в двочином виде к началу и концу блока
        else:
            msg_cypher_list.append(format(n, '0'+str(pre_size)+'b') + msg_cypher[i:i+list_size-pre_size*2] + format(n, '0'+str(pre_size)+'b'))
        n += 1
    return tuple(msg_cypher_list)

# Формирование двоичной строки из списка строк формата (№ блока + содержимое + № блока), отсортированных по возрастанию № блока
def listToMsg(msg_cypher_list, list_size, frames_count):
    msg_cypher = ''
    temp_list = []
    pre_size = len(bin(frames_count)) - 2
    # Формирование списка с кортежами формата (№ блока, содержимое) из списка строк
    for s in msg_cypher_list:
        temp_list.append(tuple((int(s[:pre_size], 2), s[pre_size:-pre_size])))
    # Сортировка блоков по возрастанию номеров
    temp_list.sort(key=lambda num: num[0])
    # Склейка двоичной строки
    for i in range(len(temp_list)):
        msg_cypher += temp_list[i][1]
    return msg_cypher

# Расчет кол-ва измененных бит после встраивания
def msgEmbedTest(msg, pos_list, frame):
    temp_frame = frame.copy()
    changes = 0
    # Перебор битов в строке
    for m in range(len(msg)):
        y, x = pos_list[m][0], pos_list[m][1]
        if msg[m] == '0':
            if temp_frame[y][x][0] % 2 == 1: # 0 == Blue
                changes += 1
        elif msg[m] == '1':
            if temp_frame[y][x][0] % 2 == 0:
                changes += 1
    return changes

# Поиск пар формата (№ кадра, № блока) с лучшим показателем для встраивания
def getBestFrames(msg_cypher_list, pos_list, frames_list):
    frames_best_list = [] # список лучших кадров для встраивания
    temp_list = []
    # Формирование списка словарей [№ кадра]{№ блока : кол-во изменений}
    for f in range(len(frames_list)):
        temp_dict = {}
        for m in range(len(msg_cypher_list)):
            temp_dict[m] = msgEmbedTest(msg_cypher_list[m], pos_list, frames_list[f])
        temp_list.append(temp_dict)
    # Поиск лучших кадров
    for m in range(len(msg_cypher_list)):
        best = [0,999999] # [№ кадра, кол-во изменений]
        for f in range(len(frames_list)):
            if (temp_list[f][m] < best[1]) and (f not in frames_best_list):
                best[0], best[1] = f, temp_list[f][m]
        frames_best_list.append(best[0])
    return tuple(frames_best_list)

# Встраивание сообщения в лучшие кадры
def msgEmbed(msg_cypher_list, pos_list, frames_list, f_b_l):
    for msg in range(len(msg_cypher_list)):
        for m in range(len(msg_cypher_list[msg])):
            y, x = pos_list[m][0], pos_list[m][1]
            if msg_cypher_list[msg][m] == '0':
                if frames_list[f_b_l[msg]][y][x][0] % 2 == 1:
                    frames_list[f_b_l[msg]][y][x][0] -= 1
            elif msg_cypher_list[msg][m] == '1':
                if frames_list[f_b_l[msg]][y][x][0] % 2 == 0:
                    frames_list[f_b_l[msg]][y][x][0] += 1
    return frames_list

# Извлечение списка строк со встроенным сообщением из кадров
def msgExtract(frames_list, pos_list):
    msg_cypher_list = []
    pre_size = len(bin(len(frames_list))) - 2
    for f in range(len(frames_list)):
        temp = ''
        for yx in range(len(pos_list)):
            y, x = pos_list[yx][0], pos_list[yx][1]
            if frames_list[f][y][x][0] % 2 == 1:
                temp += '1'
            elif frames_list[f][y][x][0] % 2 == 0:
                temp += '0'
        if temp[:pre_size] == temp[-pre_size:]:
            msg_cypher_list.append(temp)
    return msg_cypher_list

# Расчет параметра PSNR
def getPsnr(path1, path2):
    frames_list1, vid_size1 = videoToList(path1)
    frames_list2, vid_size2 = videoToList(path2)
    vid_width, vid_height = vid_size1
    frames_count = len(frames_list1)
    psnr = 0
    for f in range(len(frames_list1)):
        mse = 0
        for y in range(vid_height):
            for x in range(vid_width):
                mse += (int(frames_list2[f][y][x][0]) - int(frames_list1[f][y][x][0])) ** 2
        mse /= vid_height*vid_width
        if mse == 0:
            frames_count -= 1
        else:
            psnr += (10*math.log10((255**2)/mse))
    psnr /= frames_count
    return round(psnr, 3)

# Встраивание сообщения в LSB кадров видео
def embedding(msg_plain, plain_path, encode_path):
    # Кодирование двоичной строки
    msg_cypher = strEncode(msg_plain)
    # Получение списка BGR кадров и характеристик видео
    frames_list, vid_size = videoToList(plain_path)
    # Проверка на возможность встраивания сообщения
    canEmbed(msg_cypher, vid_size, len(frames_list))
    # Генерация списка позиций для встраивания в кадр
    pos_list = getPositions(vid_size) # (y, x)
    # Разбиение двоичной строки на список строк формата (№ блока + содержимое + № блока)
    msg_cypher_list = msgToList(msg_cypher, len(pos_list), len(frames_list))
    # Получение списка лучших кадров для встраивания
    frames_best_list = getBestFrames(msg_cypher_list, pos_list, frames_list)
    # frames_best_list = (0,1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16,17,18,19,20,21,22,23,24,25,26,27,28,29,30,31,32,33,34,35,36,37,38,39,40,41,42,43,44,45,46,47,48,49)
    # Встраивание сообщения в лучшие кадры
    frames_list = msgEmbed(msg_cypher_list, pos_list, frames_list, frames_best_list)
    # Создание видео со встроенным сообщением
    listToVideo(frames_list, vid_size, encode_path)
    return 0

# Извлечение сообщения из LSB кадров видео
def extracting(encode_path):
    # Получение списка BGR кадров и характеристик видео
    frames_list, vid_size = videoToList(encode_path)
    # Генерация списка позиций для извлечения из кадра
    pos_list = getPositions(vid_size)
    # Извлечение списка строк со встроенным сообщением из кадров
    msg_cypher_list = msgExtract(frames_list, pos_list)
    # Формирование двочной строки из списка строк формата (№ блока + содержимое + № блока)
    msg_cypher = listToMsg(msg_cypher_list, len(pos_list), len(frames_list))
    # Декодирование двочной строки
    msg_plain = strDecode(msg_cypher)
    return msg_plain

 # ---------------------------------------------------------------------------------------------------
def main():
    # Выбор встраивания/извлечения
    option = input('Для встраивания введите 1, для извлечения введите 2: ')
    while option not in '12':
        print('Неверный символ: ', option)
        option = input('Для встраивания введите 1, для извлечения введите 2: ')
    # Встраивание
    if option == '1':
        # Ввод сообщения
        msg_plain = input('Введите сообщение для встраивания в текст: ')
        # msg_plain = ''
        # for i in range(20000):
        #     msg_plain += chr(random.randrange(1040, 1103))
        # Встраивание сообщения в кадры видео
        embedding(msg_plain, plain_path, encode_path)
        # Рассчет параметра PSNR
        # psnr = getPsnr(plain_path, encode_path)
        print('Встроено сообщение \"', msg_plain, '\" в видео \"', plain_path, '\"', sep='')
        # print('Параметр PSNR равен', psnr, 'dB')
    # Извлечение
    elif option == '2':
        # Извлечение сообщения из кадров видео
        msg_plain = extracting(encode_path)
        print('Извлечено сообщение \"', msg_plain, '\" из видео \"', encode_path, '\"', sep='')
    return 0
# ----------------------------------------------------------------------------------------------------

if __name__ == "__main__":
    main()