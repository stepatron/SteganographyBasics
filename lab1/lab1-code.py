file_in = file_out = 0
file_in_path = 'text_plain.txt'
file_out_path = 'text_encrypted.txt'
size_plain = size_delta = count_plain = 0

# Проверка, хватит ли нужных символов для шифрования
def check_symbols():
	zero_count_sym = one_count_sym = zero_count_code = one_count_code = 0
	a = file_in.read(1)
	while len(a) > 0:
		if method == '1':
			if a == zero:	zero_count_sym += 1
			elif a == one:	one_count_sym += 1
		elif method == '3':
			if a == '.':	one_count_sym += 1
		a = file_in.read(1)
	for b in cypher_word:
		if b == '0':		zero_count_code += 1
		elif b == '1':		one_count_code += 1
	if method == '1':
		if one_count_code > one_count_sym:		return -1
		elif zero_count_code > zero_count_sym:	return -2
	elif method == '3':
		if one_count_code + zero_count_code > one_count_sym:	return -1
	else:	return 0

# Проверка, правильно ли указаны символы для шифрования
def check_dictionary():
	if option == 1:
		if zero not in dictionary.keys():
			print('Неверный символ: ', zero)
			return -1
		if one not in dictionary.keys():
			print('Неверный символ: ', one)
			return -1
	if option == 2:
		if zero not in dictionary.values():
			print('Неверный символ: ', zero)
			return -1
		if one not in dictionary.values():
			print('Неверный символ: ', one)
			return -1
	return 0

# Проверка, хватит ли предложений для шифрования
def check_sentence():
	count = 0
	pa = file_in.read(1)
	a = file_in.read(1)
	while len(a) > 0:
		if pa in '.?!' and a != '.': 
			count += 1
		pa = a
		a = file_in.read(1)
	if len(cypher_word) > count:	return -3
	else:	return 0

def size_file(file, file_path):
	if file != 0:	file.close()
	file = open(file_path, 'r', encoding='utf-8')
	i = a = 0
	c = file.read(1)
	while len(c) > 0:
		a += 1
		if ord(c) > 127 or ord(c) == 10:	i += 2
		else:								i += 1
		c = file.read(1)
	file.close()
	return a, i

# Завершеине работы при ошибке
def exit1():
	if file_in != 0:	file_in.close()
	if file_out != 0:	file_out.close()
	print ('exit(-1)')
	exit(-1)


# Выбор метода шифрования/дешифрования
method = input('Введите номер метода (1 - латиница, 2 - пробелы, 3 - спец. символы): ')
if method not in '123':
	print ('Неверный символ: ', method)
	exit1()

# Выбор шифрования/дешифрования
option = input('Зашифровать введите 1, расшифровать введите 2: ')
if option not in '12':
	print ('Неверный символ: ', option)
	exit1()


#--------ШИФРОВАНИЕ--------
if option == '1':

	file_in = open(file_in_path, 'r', encoding='utf-8')
	file_out = open(file_out_path, 'w', encoding='utf-8')

	plain_word = input('Введите слово для встраивания в текст: ')
	cypher_word = ''
	pc = '$'

	if method == '1':
		dictionary = dict(zip('А В Е К М Н О Р С Т Х а е о р с у х'.split(),'A B E K M H O P C T X a e o p c y x'.split()))
		zeroone = input('Введите 2 символа (А,В,Е,К,М,Н,О,Р,С,Т,Х,а,е,о,р,с,у,х) вместо "01" для шифрования: ')
		zero = zeroone[0]
		one = zeroone[1]
		if check_dictionary() == -1:	exit1
	elif method == '3':
		zero = '.'
		one = ','

	# Преобразование слова в двоичный код
	for i in plain_word: cypher_word += format(ord(i)-1024, '07b')
	# print ('Слово в двоичном коде:	', cypher_word)
	print('')

	# Проверка на нехватку символов
	if method == '1' or method == '3':		res = check_symbols()
	elif method == '2':						res = check_sentence()
	if res == -1: 
		print ('В исходном тексте не хватает символов: ', one)
		exit1()
	elif res == -2: 
		print ('В исходном тексте не хватает символов: ', zero)
		exit1()
	elif res == -3:
		print('В исходном тексте недостаточно предложений для зашифровки слова: ', plain_word)
		exit1()
	else:
		file_in.close()
		file_in = open(file_in_path, 'r', encoding='utf-8')

	#----МЕТОД ЛАТИНИЦА----
	if method == '1':

		# Разбор двоичного кода
		for word in cypher_word:
		    # Разбор исходного текста
			c = file_in.read(1)
			while len(c) > 0:
		        # Замена при нуле
				if word == '0' and c == zero:
					file_out.write(dictionary[c])
					break
				# Замена при единице
				elif word == '1' and c == one:
					file_out.write(dictionary[c])
					break
				# Пропуск
				else:
					file_out.write(c)
					c = file_in.read(1)

		# Вставка оставшейся части текста
		file_out.write(file_in.read())

		# Подсчет объема встраивания
		count_plain = size_file(file_in, file_in_path)[0]
		size_plain = size_file(file_in, file_in_path)[1]
		size_delta = len(cypher_word)
		print('Заменено символов:	', size_delta, ' из ', count_plain, ' исходных символов')
		print('Изменение размера:	', size_plain, ' -> ', size_plain-size_delta, '	| -', size_delta, ' байт')


	#----МЕТОД ПРОБЕЛЫ----
	elif method == '2':

		# Разбор двоичного кода
		for word in cypher_word:
			# Разбор исходного текста
			c = file_in.read(1)
			while len(c) > 0:
				if word == '1' and pc in '.?!' and c != '.':
					file_out.write(' ')
					file_out.write(c)
					pc = c
					break
				elif word == '0' and pc in '.?!' and c != '.':
					file_out.write(c)
					pc = c
					break
				else:
					file_out.write(c)
					pc = c
					c = file_in.read(1)

		# Вставка оставшейся части текста
		file_out.write(file_in.read())

		# Подсчет объема встраивания
		count_plain = size_file(file_in, file_in_path)[0]
		size_plain = size_file(file_in, file_in_path)[1]
		size_delta = cypher_word.count('1')
		print('Пробелов добавлено:	', size_delta, ' к ', count_plain, ' исходным символам')
		print('Изменение размера:	', size_plain, ' -> ', size_plain+size_delta, '	| +', size_delta, ' байт')


	#----МЕТОД СПЕЦ. СИМВОЛЫ----
	elif method == '3':

		# Разбор двоичного кода
		for word in cypher_word:
		    # Разбор исходного текста
			c = file_in.read(1)
			while len(c) > 0:
		        # Замена при единице
				if word == '1' and c == '.':
					file_out.write(chr(803))
					# file_out.write(' ')
					break
				# Замена при нуле
				elif word == '0' and c == '.':
					file_out.write('.')
					break
				# Пропуск
				else:
					file_out.write(c)
					c = file_in.read(1)

		# Вставка оставшейся части текста
		file_out.write(file_in.read())

		# Подсчет объема встраивания
		count_plain = size_file(file_in, file_in_path)[0]
		size_plain = size_file(file_in, file_in_path)[1]
		size_delta = cypher_word.count('1')
		print('Замена спец. символов:	', size_delta, ' из ', count_plain, ' исходных символов')
		print('Изменение размера:	', size_plain, ' -> ', size_plain+size_delta, '	| +', size_delta, ' байт')


#--------ДЕШИФРОВАНИЕ--------
elif option == '2':

	file_out = open(file_in_path, 'w', encoding='utf-8')
	file_in = open(file_out_path, 'r', encoding='utf-8')

	cypher_word = string = plain_word = ''

	#----МЕТОД ЛАТИНИЦА----
	if method == '1':

		dictionary = dict(zip('A B E K M H O P C T X a e o p c y x'.split(),'А В Е К М Н О Р С Т Х а е о р с у х'.split()))
		zeroone = input('Введите 2 символа (А,В,Е,К,М,Н,О,Р,С,Т,Х,а,е,о,р,с,у,х) вместо "01" для дешифрования: ')
		zero = zeroone[0]
		one = zeroone[1]
		if check_dictionary() == -1:	exit1

		# Дешифрование двочиного кода
		c = file_in.read(1)
		while len(c) > 0:
			if c in dictionary.keys():
				if dictionary[c] == zero:
					cypher_word += '0'
				elif dictionary[c] == one:
					cypher_word += '1'
				file_out.write(dictionary[c])
			else:
				file_out.write(c)
			c = file_in.read(1)

	#----МЕТОД ПРОБЕЛЫ----
	elif method == '2':

		# Дешифрование двочиного кода
		ppc = pс = ''
		ppc = file_in.read(1)
		pc = file_in.read(1)
		c = file_in.read(1)
		while len(c) > 0:
			file_out.write(pc)
			if ppc in '.?!' and pc == ' ' and c == ' ':
				cypher_word += '1'
				c = file_in.read(1)
			elif ppc in '.?!' and (pc == ' ' or pc == chr(10)) and c != ' ':
				cypher_word += '0'
			ppc = pc
			pc = c
			c = file_in.read(1)

	#----МЕТОД СПЕЦ. СИМВОЛЫ----
	elif method == '3':

		# Дешифрование двочиного кода
		pc = file_in.read(1)
		c = file_in.read(1)
		while len(c) > 0:
			if pc == chr(803) and c == ' ':
				cypher_word += '1'
				file_out.write('.')
				c = file_in.read(1)
			elif pc == '.':
				cypher_word += '0'
				file_out.write(pc)
			else:
				file_out.write(pc)
			pc = c
			c = file_in.read(1)

	# Преобразование двоичного кода
	for i in range(len(cypher_word)):
		string += cypher_word[i]
		if len(string) == 7 and string != '0000000':
			plain_word += chr(int(string, 2)+1024)
			string = ''

	print ('Расшифрованное слово:', plain_word)

file_in.close()
file_out.close()
exit(0)
