def count_fizz_buzz(n): 
	fizz_buzz = 0
	fizz = 0
	buzz = 0

	for num in n: 
		if n % 3 == 0 and n % 5 == 0: 
			fizz_buzz += 1
		elif n%3 == 0: 
			fizz +=1
		elif n%5 == 0: 
			buzz +=1

	return fizz, buzz, fizz_buzz


