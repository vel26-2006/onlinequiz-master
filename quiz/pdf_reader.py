import fitz
import re
from .models import Question


def extract_questions_from_pdf(pdf_path, course):
    doc = fitz.open(pdf_path)

    text = ""
    for page in doc:
        text += page.get_text()

    lines = [line.strip() for line in text.split("\n") if line.strip()]

    i = 0

    while i < len(lines):

        q = re.match(r"(\d+)\.\s*(.*)", lines[i])

        if q:
            question = q.group(2)

            option1 = re.sub(r"^[A-D]\)\s*", "", lines[i + 1])
            option2 = re.sub(r"^[A-D]\)\s*", "", lines[i + 2])
            option3 = re.sub(r"^[A-D]\)\s*", "", lines[i + 3])
            option4 = re.sub(r"^[A-D]\)\s*", "", lines[i + 4])

            answer_line = lines[i + 5]

            match = re.search(r"Correct Answer:\s*([A-D])", answer_line)

            if match:
                ans = match.group(1)
            else:
                ans = "A"

            answer_map = {
                "A": "Option1",
                "B": "Option2",
                "C": "Option3",
                "D": "Option4",
            }

            Question.objects.create(
                course=course,
                marks=1,
                question=question,
                option1=option1,
                option2=option2,
                option3=option3,
                option4=option4,
                answer=answer_map[ans],
            )

            i += 6

        else:
            i += 1