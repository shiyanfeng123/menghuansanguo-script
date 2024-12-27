import hashlib
import itertools
import string
import threading


def md5_crack(hash_to_crack, length, charset, result):
	for combination in itertools.product(charset, repeat=length):
		password = ''.join(combination)
		word_hash = hashlib.md5(password.encode('utf-8')).hexdigest()
		if word_hash == hash_to_crack:
			result.append(password)
			break


def main():
	hash_to_crack = "9634307f1d8ccca68d6e9416d21cc988e603f498c76f01a75066da4257cc5315"
	max_length = int(input("请输入最大密码长度: "))
	# charset = string.ascii_lowercase + string.digits
	charset = string.digits
	num_threads = 4  # 线程数
	threads = []
	result = []

	for length in range(1, max_length + 1):
		for i in range(num_threads):
			thread = threading.Thread(target=md5_crack, args=(hash_to_crack, length, charset, result))
			threads.append(thread)
			thread.start()

		for thread in threads:
			thread.join()

		if result:
			break

	if result:
		print(f"破解成功，密码是: {result[0]}")
	else:
		print("破解失败，未找到匹配的密码。")


if __name__ == "__main__":
	main()
