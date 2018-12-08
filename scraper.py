'''
Code to do the majority of the web scraping by Evan Hughes @ https://github.com/wisebaldone/uq-secat

I (Blake Bodycote) modified the code to get certain pieces of data such as question/answer info
and to make it simple to import the scraped data into a MySQL database. 
'''

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

from random import randint
import time
import json
import os
import sys

from utils import utils

print("UQ-SECAT Scraper\n"
      "-----------------")
print("Please Do not Run this aggressively\n")
print("Loading WebBrowser...")

driver = webdriver.Chrome()
driver.get("http://www.pbi.uq.edu.au/clientservices/SECaT/embedChart.aspx")
driver.implicitly_wait(10)
WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.ID, "RadTabStrip1")))

print("Preparing to fetch data.")
driver.maximize_window()
time.sleep(5)

top_level = driver.find_element_by_class_name("rtsLevel1")
elements = top_level.find_elements_by_class_name("rtsLink")

level1_num = len(elements)
filename = "secats.JSON"
f = open(filename, 'w')

# Initiate web scraping and store all course secat data in a JSON file
for level1 in range(0, level1_num):
    level1_bar = driver.find_element_by_class_name("rtsLevel1")
    level1_elements = level1_bar.find_elements_by_class_name("rtsLink")
    level1_elements[level1].click()

    lowest_counter = 0

    level2_bar = driver.find_element_by_class_name("rtsLevel2")
    level2_elements = level2_bar.find_elements_by_class_name("rtsLink")
    level2_num = len(level2_elements)

    for level2 in range(0, level2_num):
        level2_bar = driver.find_element_by_class_name("rtsLevel2")
        level2_elements = level2_bar.find_elements_by_class_name("rtsLink")
        level2_elements[level2].click()

        level3_bar = driver.find_element_by_class_name("rtsLevel3").find_elements_by_class_name("rtsUL")[level2]
        level3_elements = level3_bar.find_elements_by_class_name("rtsLink")
        level3_num = len(level3_elements)
        for level3 in range(0, level3_num):
            level3_bar = driver.find_element_by_class_name("rtsLevel3").find_elements_by_class_name("rtsUL")[level2]
            level3_elements = level3_bar.find_elements_by_class_name("rtsLink")
            level3_elements[level3].click()

            level4_bar = driver.find_element_by_class_name("rtsLevel4").find_elements_by_class_name("rtsUL")[lowest_counter]
            level4_elements = level4_bar.find_elements_by_class_name("rtsLink")
            level4_num = len(level4_elements)

            for level4 in range(0, level4_num):
                level4_bar = driver.find_element_by_class_name("rtsLevel4").find_elements_by_class_name("rtsUL")[lowest_counter]
                level4_elements = level4_bar.find_elements_by_class_name("rtsLink")

                level4_elements[level4].click()

                # Get Stats
                raw = driver.execute_script("return courseSECATData;")
                raw_description = driver.execute_script("return title;")
                enrolled = driver.find_element_by_id("lblNoEnrolled").text
                responses = driver.find_element_by_id("lblNoResponses").text
                rate = driver.find_element_by_id("lblRespRate").text

                course_info = utils.get_course_question_data(raw, raw_description, enrolled, responses, rate)

                f.write(str(course_info) + "\n")

            time.sleep(randint(0,2))
            lowest_counter += 1
    time.sleep(randint(60,120))
time.sleep(5)
print("Closing Web Browser")
driver.close()
f.close()


#Convert all of our collected JSON data to a MySQL friendly database import
sql_string = "CREATE TABLE Course (CourseID varchar(10), Name varchar(255), PRIMARY KEY (CourseID)); \n"
sql_string += "CREATE TABLE CourseSemester ( ID varchar(20), CourseID varchar(10), Semester int, Year int, Enrolled int, Responses int, PRIMARY KEY (ID), FOREIGN KEY (CourseID) REFERENCES Course(CourseID)); \n"
sql_string += "CREATE TABLE Question (ID int, Name varchar(50), PRIMARY KEY (ID) ); \n"
sql_string += "CREATE TABLE QuestionAnswers (ID int AUTO_INCREMENT, QuestionID int, CourseSemID varchar(20), StronglyDisagree int, Disagree int, NeitherAgreeOrDisagree int, Agree int, StronglyAgree int, PRIMARY KEY (ID), FOREIGN KEY (QuestionID) REFERENCES Question(ID), FOREIGN KEY (CourseSemID) REFERENCES CourseSemester(ID));  \n"

f = open(filename, 'r')
courses = {}
count=0
question_ids = {}
for i in f:
    print(i)
    string_to_add = ""
    json_data = json.loads(i)
    course = json_data["course"]
    name = json_data["name"]
    enrolled = json_data["enrolled"]
    responses = json_data["responses"]
    semester = json_data["sem"]
    year = json_data["year"]
    questions = json_data["questions"]
    course_sem_year = str(course)+str(semester)+str(year)
    if(count == 0):
        for question in list(questions.keys()):
            x = question.split(": ")
            question_ids[question] = (x[0][1],str(x[1]))
            string_to_add += 'insert into Question values ({}, "{}"); \n'.format(x[0][1],x[1])

    if not (course in courses):
        string_to_add += 'insert into Course values ("{}","{}"); \n'.format(course,name)
        courses[course] = 1
    string_to_add += 'insert into CourseSemester values ("{}","{}",{},{},{},{}); \n'.format(course_sem_year ,course, semester, year, enrolled, responses)
    
    for question in questions:
        question_answers = {}
        answers = questions[question]
        for answer in answers:
            question_answers[answer["answer"]] = answer["value"]
        print(question_answers)
        string_to_add += 'insert into QuestionAnswers values (default,{},"{}",{},{},{},{},{}); \n'.format(question_ids[question][0],course_sem_year,question_answers["StronglyDisagree"],question_answers["Disagree"],question_answers["NeitherAgreeOrDisagree"],question_answers["Agree"],question_answers["StronglyAgree"])

    sql_string += string_to_add
    count+=1
f.close()

f = open("secat_data.sql", "w")
f.write(sql_string)
f.close()