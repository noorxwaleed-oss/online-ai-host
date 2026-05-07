
import json
def tojson (text):
    
  data = json.loads(text.content)
  return data

def print_script(script):
  print(script["total_pages"])
  for page in script["pages"]:
      print(f"Page {page['page_number']}:")
      print(page["content"])
      print("\n---\n")