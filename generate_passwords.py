import random
import string


def generate_password(length=8):
	# 定义密码字符集，包括小写字母、大写字母、数字和特殊字符
	# characters = string.ascii_letters + string.digits + string.punctuation
	# 数字
	characters = string.digits
	# 定义密码字符集，包括小写字母、大写字母、数字
	# characters = string.ascii_letters + string.digits
	return ''.join(random.choice(characters) for _ in range(length))


def generate_password_list(num_passwords=100000, length=8, output_file='dictionary.txt'):
	with open(output_file, 'w', encoding='utf-8') as file:
		for _ in range(num_passwords):
			password = generate_password(length)
			file.write(password + '\n')


if __name__ == "__main__":
	generate_password_list()
