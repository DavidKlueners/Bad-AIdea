import os
import time
import csv

import openai
from flask import Flask, redirect, render_template, request, url_for

app = Flask(__name__)
openai.api_key = os.getenv("OPENAI_API_KEY")

#---------------CSV import
text_list = []
issue_list = []

with open('./static/text_data_merged.csv') as csv_file:
    csv_reader = csv.reader(csv_file, delimiter=',')
    line_count = 0
    for row in csv_reader:
        if line_count == 0:
            #print(f'Column names are {", ".join(row)}')
            line_count += 1
        else:
            text_list.append(row[1])
            issue_list.append(row[2])
            line_count += 1
   
#print(len(issue_list))


# -------------search engine
# uploading a file
response = openai.File.create(
  file=open("./static/files.jsonl"),
  purpose='search'
)
file_id = response.id
time.sleep(5)

#print(openai.File.list())
#print(len(openai.File.list()))
#print(openai.File.retrieve(file_id))


#-------------completion engine setup
@app.route("/", methods=("GET", "POST"))
def index():
    if request.method == "POST":
        AI_idea = request.form["idea"]
        text = issue_list_query(AI_idea)
        response = openai.Completion.create(
            engine="text-davinci-002",
            prompt=generate_prompt(AI_idea, text),
            temperature=0.6,
            max_tokens =1000
        )
        return redirect(url_for("index", result=response.choices[0].text))

    result = request.args.get("result")
    print(result)
    return render_template("index.html", result=result)

def issue_list_query(AI_idea):
    # querying the issue list based on the AI idea
    response = openai.Engine("davinci").search(
    documents=issue_list[:200],
    #file=file_id,
    query=AI_idea,
    )
    print(type(response))
    sorted_response = sorted(response["data"], key=lambda kv: kv["score"])
    #print(sorted_response[-6:])

    #print(issue_list[26])

    top_five = sorted_response[-5:]

    prompt_text = ""
    for d in top_five:
        cur_doc_num = d["document"]
        cur_issue_text= issue_list[cur_doc_num]
        prompt_text = prompt_text + cur_issue_text + "\n"
    
    return prompt_text

#generating the prompt for the completion engine based on the users idea input and the issues that were matched to the idea
def generate_prompt(AI_idea, prompt_text):
    return f"""Give ten examples on the risks associated with the following idea: {AI_idea}
    \n {prompt_text}
    """
