#!/usr/bin/python3
# -*- coding: utf-8 -*-
# vim: set noet ci pi sts=0 sw=4 ts=4:
from selenium import webdriver
from selenium.webdriver.support.select import Select
import socket
import argparse


def get_xmax(driver) -> "maximum courses of study":
	"""gets the maximum number of indexes for course of study choice"""
	# counts the possible courses
	xmax = 0
	for option in driver.find_element_by_name(
		"course").find_elements_by_tag_name('option'):
		xmax += 1
	return xmax - 1


def get_ymax(driver) -> "maximum semester":
	"""gets the maximum number of indexes for semster choice"""
	ymax = 0
	# counts the possible semesers
	for option in driver.find_element_by_name(
		"semester").find_elements_by_tag_name('option'):
		ymax += 1
	return ymax - 1


def study_choice(driver, x):
	"""routine for iteration of study_choice"""
	# gets the dropdown element by its name selects course via select_by_index
	Select(driver.find_element_by_name("course")).select_by_index(x)

	# clicks submit button
	driver.find_element_by_xpath("//*[@id='main']/form/input").click()


def semester_choice(driver, y):
	"""routine for iteration of semester_choice"""
	# gets the dropdown element by its name selects semester via select_by_index
	Select(driver.find_element_by_name("semester")).select_by_index(y)

	# clicks "wählen und weiter" Button
	driver.find_element_by_xpath("//*[@id='main']/form/input").click()


def module_choices(driver):
	"""routine for iteration of module_choices"""
	listFilled = False
	# clicks every checkbox in "Empfohlen"
	for checkbox in driver.find_elements_by_xpath("//*[@name='choosen_modules']"):
		# double clicks checkbox
		checkbox.click()
		checkbox.click()
		listFilled = True
	if not listFilled:
		print("WARNING: Modulelist empty @ module_choices Empfohlen")

	listFilled = False
	# clicks every checkbox "Studiengang"
	for checkbox in driver.find_elements_by_xpath(
		"//*[@name='study_course_modules']"):
		checkbox.click()
		listFilled = True
	if not listFilled:
		print("WARNING: Modulelist empty @ module_choices Studiengang")

	listFilled = False
# 	# clicks every checkbox "Alle Module"
# 	for checkbox in driver.find_elements_by_xpath("//*[@name='all_modules']"):
# 		checkbox.click()
# 		listFilled = True
# 	if not listFilled:
# 		print("WARNING: Modulelist empty @ module_choices Alle Module")

	# clicks "wählen und weiter" Button
	driver.find_element_by_xpath("//*[@id='main']/form/dd/input").click()


def lv_choices(driver):
	"""routine for iteration of lv_choices"""
	listFilled = False
	for checkbox in driver.find_elements_by_xpath(
		"//*[@id='main']/form/li/dd/ul/li/input"):
		checkbox.click()
		listFilled = True
	if not listFilled:
		print("WARNING: Modulelist empty @ lv_choices")

	# clicks "wählen und weiter" Button
	driver.find_element_by_xpath("//*[@id='main']/form/dd/input").click()
	# clicks "wählen und weiter" Button
	driver.find_element_by_xpath("//*[@id='main']/form/dd/input").click()


if __name__ == "__main__":
	# parses arguments
	parser = argparse.ArgumentParser()
	parser.add_argument("-p", "--port", default="1350",
		help="Port of webserver to test")
	parser.add_argument("-u", "--url", metavar="ADDRESS",
		default="pcai042.informatik.uni-leipzig.de",
		help="Hostname of webserver to test")
	parser.add_argument("-d", "--driver", metavar="BROWSER", default="firefox",
		help="Browser to test with")
	args = parser.parse_args()

	# choose port
	port = args.port
	# set url
	url = args.url
	# sets url with port an source
	source = url + ":" + port

	# Starts driver (browser needs to be installed)
	if args.driver.lower() == "firefox" or args.driver.lower() == "f":
		driver = webdriver.Firefox()
	elif args.driver.lower() == "chrome" or args.driver.lower() == "c":
		driver = webdriver.Chrome()
	elif args.driver.lower() == "opera" or args.driver.lower() == "o":
		driver = webdriver.Opera()
	else:
		print("Given driver-value not found. Try another browser.")
		exit()

	# course iterator
	x = 0
	# semester iterator
	y = 0
	# course iterator maximum
	xmax = 0
	# semester iterator maximum
	ymax = 0

	while(True):
		# Studiengangwahl
		driver.get(source + "/study_choice")

		xmax = get_xmax(driver)
		study_choice(driver, x)
		ymax = get_ymax(driver)
		semester_choice(driver, y)
		module_choices(driver)
		lv_choices(driver)

		# increments semester iterator
		y += 1
		# increments course iterator if semester iterator reached its maximum
		if(y == ymax):
			y = 0
			if(xmax == x):
				break
			x += 1

	# stops driver
	driver.close()
