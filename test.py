def grid(width,height,func=lambda x,y:(x,y)):
	return [[func(x,y) for x in xrange(width)] for y in xrange(height)]

if __name__ == '__main__':
	print grid(640//16,480//16,lambda x,y:(x*16,y*16))
