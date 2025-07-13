from browserbase import Browserbase
import os
from dotenv import load_dotenv

load_dotenv()

bb = Browserbase(api_key=os.environ["BROWSERBASE_API_KEY"])

def create_context():
    context = bb.contexts.create(project_id=os.environ["BROWSERBASE_PROJECT_ID"])
    return context.id

context_id = create_context()
print("Context ID:", context_id)