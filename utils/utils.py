import json

def sum_digits(digit):
    return sum(int(x) for x in digit if x.isdigit())

def get_course_question_data(raw, raw_description, enrolled, responses, rate):
    question_keys = {"5": "StronglyDisagree", "4": "Disagree", "3": "NeitherAgreeOrDisagree", "2": "Agree", "1":"StronglyAgree"}
    returned_data={}
    
    course = raw[0]["COURSE_CD"]
    try:
        course_name = raw_description.split(":")[0]
    except:
        course_name = "untitled"
    returned_data["name"] = course_name
    year = raw[0]["SEMESTER_DESCR"].split(",")[1].strip()
    returned_data["course"] = course
    returned_data["enrolled"] = enrolled
    returned_data["responses"] = responses
    returned_data["response_rate"] = rate

    if "Summer" in raw[0]["SEMESTER_DESCR"]:
        semester = 3
    else:
        semester = int(raw[0]["SEMESTER_DESCR"].split(" ")[1].split(",")[0])
    returned_data["sem"]=semester
    returned_data["year"]=year
    questions = {}
    for i in raw:
        questions[i["QUESTION_NAME"]] = []

    for i in raw:
        answer = {"answer":question_keys[i["ANSWER"][0]], "number_of_answers": i["ANSWERED_QUESTION"], "value" : i["VALUE"], "percent_answer": i["PERCENT_ANSWER"]}
        questions[i["QUESTION_NAME"]].append(answer)
    returned_data["questions"] = questions
    return json.dumps(returned_data)
