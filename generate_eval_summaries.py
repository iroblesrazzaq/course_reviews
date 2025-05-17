# %%
%pip install google-generativeai PyMuPDF pandas


# %%
import google.generativeai as genai

genai.configure(api_key="AIzaSyBiI-w6nj6XsVvxqtdwFQbeaq9RSyUdcW4")

model = genai.GenerativeModel(model_name="models/gemini-1.5-flash")

# %%
prompt = """You are an expert course feedback reviewer for a university. Your primary task is to analyze the provided course review PDF document (which includes text and visual elements like charts) and generate a structured summary.

Your output MUST strictly follow the format and constraints outlined below. When extracting information, pay close attention to both the textual commentary and any relevant charts or tables within the PDF, especially for quantitative data like time commitments.

OUTPUT FORMAT AND CONSTRAINTS:

1.  **Graded components:**
    *   List the main graded elements of the course. If percentages are mentioned in text or tables, include them.

2.  **Feedback summary:**
    *   Provide a concise 2-3 sentence summary of the overall student feedback, incorporating insights from both text and any relevant visuals.

3.  **To get a good grade:**
    *   This section MUST contain a maximum of 3 bullet points.
    *   List actionable advice based on textual feedback and any visual cues about effort or focus.

4.  **You should take this class if:**
    *   This section MUST contain a maximum of 3 bullet points.
    *   One bullet point SHOULD specify the **average outside-of-class time commitment**. Prioritize data directly extracted from charts (e.g., "How many hours per week..." charts). If no chart is present or interpretable for this, use textual mentions.
    *   Other points should focus on who the course is suitable for based on workload tolerance, learning style preferences, or academic needs, considering all PDF content.

5.  **You shouldn't take this class if:**
    *   This section MUST contain a maximum of 3 bullet points.
    *   List reasons or profiles of students for whom this course might not be a good fit, considering all PDF content.

--- EXAMPLES START ---

--- EXAMPLE 1: CMSC 14400 ---
[This is the desired output if the input PDF was for CMSC 14400.]

CMSC 14400 1 - Systems Programming II - Instructor(s) - Haryadi Gunawi, Junchen Jiang
Project Title: College Course Feedback - Winter 2025
Number Enrolled: 61
Number of Responses: 33

Graded components: Midterm, final, projects, homeworks.

Feedback summary:
Some students found it moderately difficult, others very difficult, with mixed reviews on course design. Professor Jiang's lectures were generally liked, while Professor Gunawi's flipped classroom format was largely disliked. Most students spent 5-15 hours per week outside class (as indicated by the time commitment chart and comments).

To get a good grade:
*   Start projects very early as they are time-consuming.
*   Master the material thoroughly for exams, as they are key differentiators.
*   Utilize TA office hours effectively for help with challenging projects.

You should take this class if:
*   You are prepared to spend around 5-15 hours per week outside of class, according to the student-reported time commitment chart.
*   You need to fulfill a CS requirement and are ready for a challenging, time-intensive course.
*   You can adapt to different teaching styles, including a potentially less popular flipped classroom for part of the course.

You shouldn't take this class if:
*   You are looking for a lightly demanding elective and are not a CS major.
*   You strongly dislike flipped classroom formats or inconsistent teaching approaches.
*   You struggle with time management for large, demanding projects.
--- EXAMPLE 1 END ---

--- EXAMPLE 2: BIOS 25108 ---
[This is the desired output if the input PDF was for BIOS 25108.]

BIOS 25108 1 - Cancer Biology - Instructor(s) - Alexander Muir, Andrea Piunti
Project Title: College Course Feedback - Autumn 2024
Number Enrolled: 24
Number of Responses: 12

Graded components: Group final project (50%), take-home midterm (20%), participation (25%), weekly homework (5%).

Feedback summary:
Cancer Biology was generally perceived as a manageable and "chill" course with a fair workload, supported by student comments and time commitment charts. Attending lectures and starting the final project early were key to success.

To get a good grade:
*   Attend lectures regularly and engage with the material presented.
*   Start working on the group final project early to manage the workload effectively.
*   Complete the weekly homework assignments, which are graded on completion.

You should take this class if:
*   You are prepared to spend around 5 hours per week outside of class, as suggested by the time commitment chart showing a majority in the <5 or 5-10 hour range.
*   You are looking for an interesting biology elective that is manageable alongside other courses.
*   You appreciate a course structure with clear grading components and straightforward paths to success.

You shouldn't take this class if:
*   You are seeking an intensely rigorous course that demands significantly more than 5-10 hours weekly.
*   You dislike group projects, as the final project is a significant component.
*   You prefer courses with a primary focus on high-stakes exams over projects and participation.
--- EXAMPLE 2 END ---

--- EXAMPLE 3: SOCI 20002 ---
[This is the desired output if the input PDF was for SOCI 20002.]

SOCI 20002 1 - Society, Power and Change - Instructor(s) - Julian Go III
Project Title: College Course Feedback - Autumn 2024
Number Enrolled: 21
Number of Responses: 8

Graded components: Weekly memos (based on readings and lectures).

Feedback summary:
This course is considered an interesting and relatively easy introduction to sociological ideas, with no prior background required. Lectures by Professor Go are crucial for understanding dense readings, and weekly memos assess comprehension.

To get a good grade:
*   Attend lectures, as they are key to understanding complex readings and theories.
*   Diligently complete the weekly memos, demonstrating your understanding of both readings and lecture takeaways.
*   Engage with the material sufficiently to articulate insights in your written memos.

You should take this class if:
*   You are prepared to spend around 5-10 hours per week on readings and memo preparation, as indicated by the time commitment chart.
*   You want an accessible introduction to sociology that doesn't require prior knowledge.
*   You appreciate clear lectures that simplify complex theoretical material.

You shouldn't take this class if:
*   You dislike courses with a significant reading load, even if lectures help clarify.
*   You are not keen on weekly written assignments (memos) as the primary assessment.
*   You are looking for a highly quantitative or data-driven sociology course.
--- EXAMPLE 3 END ---

--- EXAMPLE 4: STAT 22200 ---
[This is the desired output if the input PDF was for STAT 22200.]

STAT 22200 1, STAT 22200 1 - Linear Models and Experimental Design - Instructor(s) - Yibi Huang
Project Title: College Course Feedback - Spring 2024
Number Enrolled: 91
Number of Responses: 31

Graded components: Midterm, final, twice weekly homeworks (psets).

Feedback summary:
The course is generally considered easy, especially for stats majors. Lecture slides and recorded lectures are key, highly praised resources. Professor Yibi Huang is mostly well-regarded, though some found the teaching less engaging; workload consists of frequent homeworks that can feel like busy work.

To get a good grade:
*   Stay on top of the twice-weekly homework assignments.
*   Utilize the comprehensive lecture slides and recorded lectures extensively for learning and exam preparation.
*   Ensure you understand how to apply concepts in R, as it's used in the course.

You should take this class if:
*   You are prepared to spend around 5-10 hours per week outside of class on coursework (this was the most common time reported on the chart).
*   You need a stats elective that is generally considered manageable, particularly with prior stats experience, and appreciate well-structured self-study materials.
*   You are comfortable with a consistent workload of application-focused homework and value flexibility from recorded lectures.

You shouldn't take this class if:
*   You dislike frequent homework assignments, even if the material isn't overly complex.
*   You prefer highly dynamic, Socratic-style in-person lectures over a slide-based, hybrid approach.
*   You are looking for a course with very deep theoretical engagement rather than a focus on application and computation.
--- EXAMPLE 4 END ---

--- EXAMPLES END ---

Now, analyze the PDF document that has been provided as a separate content part in this API call. Use all information within that PDF (text, charts, tables, etc.) to generate the structured summary according to the instructions and the pattern demonstrated in the examples above.
     
       """

# %%
with open("/Users/miguelsanders/Downloads/math184.pdf", "rb") as f:
    pdf_bytes = f.read()

response = model.generate_content(
    [
        prompt,  
        {"mime_type": "application/pdf", "data": pdf_bytes}
    ]
)



print(response.text)



# %%
with open("/Users/miguelsanders/Downloads/ling25001.pdf", "rb") as f:
    pdf_bytes = f.read()

response = model.generate_content(
    [
        prompt,  
        {"mime_type": "application/pdf", "data": pdf_bytes}
    ]
)



print(response.text)

# %%
import os
import pandas as pd

pdf_folder = "/Users/miguelsanders/Desktop/vals/"
output_csv = "course_eval_summaries.csv"

if not os.path.exists(output_csv):
    pd.DataFrame(columns=["file_path", "summary"]).to_csv(output_csv, index=False)

# load existing
existing = pd.read_csv(output_csv)



# go through each PDF in the folder
for filename in os.listdir(pdf_folder):
    if filename.endswith(".pdf"):
        pdf_path = os.path.join(pdf_folder, filename)

        # skip already summarized
        if pdf_path in existing["file_path"].values:
            continue

        print(f"Processing: {pdf_path}")
        with open(pdf_path, "rb") as f:
            pdf_bytes = f.read()

        try:
            response = model.generate_content([
                prompt,
                {"mime_type": "application/pdf", "data": pdf_bytes}
            ])
            summary = '"' + response.text.strip().replace('\n', '\r') + '"'



            # save to CSV
            new_row = pd.DataFrame([{
                "file_path": pdf_path,
                "summary": summary
            }])
            existing = pd.concat([existing, new_row], ignore_index=True)
            existing.to_csv(output_csv, index=False)
            print("Saved ✅\n")
        except Exception as e:
            print(f"Error processing {filename}: {e}")



