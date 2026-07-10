import fitz
import re
from .models import Question
import fitz
import re
from .models import Question

def extract_questions_from_pdf(pdf_path, course):
    doc = fitz.open(pdf_path)
    text = ""

    for page in doc:
        text += page.get_text()

    lines = [line.strip() for line in text.split("\n") if line.strip()]

    questions = []
    answers = {}
    answer_section = False

    i = 0
    while i < len(lines):

        if lines[i].lower() == "answer key":
            answer_section = True
            i += 1
            continue

        if answer_section:
            m = re.match(r"(\d+)\.\s*([A-D])", lines[i])
            if m:
                answers[int(m.group(1))] = m.group(2)
            i += 1
            continue

        q = re.match(r"(\d+)\.\s*(.*)", lines[i])
        if q:
            number = int(q.group(1))
            question = q.group(2)

            option1 = lines[i+1][3:]
            option2 = lines[i+2][3:]
            option3 = lines[i+3][3:]
            option4 = lines[i+4][3:]

            questions.append({
                "number": number,
                "question": question,
                "option1": option1,
                "option2": option2,
                "option3": option3,
                "option4": option4,
            })

            i += 5
        else:
            i += 1

    for q in questions:

        ans = answers.get(q["number"], "A")

        if ans == "A":
            answer = "Option1"
        elif ans == "B":
            answer = "Option2"
        elif ans == "C":
            answer = "Option3"
        else:
            answer = "Option4"

        Question.objects.create(
            course=course,
            marks=1,
            question=q["question"],
            option1=q["option1"],
            option2=q["option2"],
            option3=q["option3"],
            option4=q["option4"],
            answer=answer
        )