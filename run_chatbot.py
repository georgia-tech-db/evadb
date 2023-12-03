import argparse
from convert_instructions_to_pdf import *
import os
from llama_index import VectorStoreIndex, SimpleDirectoryReader

os.environ["OPENAI_API_KEY"] = "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"
parser = argparse.ArgumentParser(description='A chatbot for EvaDB')

parser.add_argument("--reload_docs", help="Reload all the RST files and rebuild the index")

args = parser.parse_args()

reload_docs_flag = args.reload_docs


if reload_docs_flag == "True":
    print("Started reloading the docs")
    convert_instr_to_pdf()
    print("Finished reloading docs")

#llama
print("Creating the Llama index.....")
documents = SimpleDirectoryReader("doc_pdf/").load_data()
index = VectorStoreIndex.from_documents(documents)

query_engine = index.as_query_engine()

print("Finished Creating the Llama index....")


while(True):
    print("Welcome to EvaDB ")
    print("Please enter your query. Enter 1 to exit the chatbot")

    user_query = input()

    if user_query == "1":
        break

    else:
        response = query_engine.query(user_query)
        print(response)


print("Terminating the chatbot.. See you next time!")


