from math import sin, pi

def drange(start, stop, step):
	r = start
	while r < stop:
		yield r
		r += step

def approx_value_of(value, n):
	return round(value * n) / n

def map_value(value, max_value = 5, bit_length = 8):
	return (value / max_value) * (2 ** bit_length - 1)

def func(t, f):
	return 2 * sin(2 * pi * f * t) + 2

step = 0.001 #delay
t = [v for v in drange(0, 0.5, step)]
u = [int(map_value(approx_value_of(func(i, 10), 100))) for i in t]

print len(u)


s =  "{"
for y in u:
	s +=  str(y) + ', '
	
s += "};"

print s