from hot_calculator import calc_hot

import threading

calc_time = 60
calc_timer = None

def calc_func():
	print("thread start!")
	calc_hot()
	global calc_timer
	calc_timer = threading.Timer(calc_time, calc_func)
	calc_timer.start()


if __name__ == "__main__":
	calc_func()

