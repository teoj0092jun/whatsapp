from openai import OpenAI
import config
from utils import get_thread_id_from_recipient_id, update_thread_id_for_recipient_id


client = OpenAI(
    api_key=config.OPENAI_API_KEY
)

def ask_openai_assistant(query: str, recipient_id: str) -> str:
    try:
        # Ensure thread ID remains the same even after run is restarted, keeping any user interaction
        thread_id = "thread_BXxGmRfAejMA1YBrN1agBmGT"
        ##thread_id = get_thread_id_from_recipient_id(recipient_id=recipient_id)
        if thread_id:
            print("Thread ID Found")
            thread = client.beta.threads.retrieve(thread_id=thread_id)
        else:
            print("Creating Thread ID")
            thread = client.beta.threads.create()
            update_thread_id_for_recipient_id(recipient_id=recipient_id, thread_id=thread.id)
        print(f"Thread ID --> {thread}")
        print(f"Recipient ID --> {recipient_id}")

        _ = client.beta.threads.messages.create(
            thread_id=thread.id,
            content=query,
            role="user"
        )

        run = client.beta.threads.runs.create(
            thread_id=thread.id,
            assistant_id=config.ASSISTANT_ID,
            instructions="""
            Replies are in a friendly tone and needs to be made with reference to existing knowledge provided in the files where possible.
            Do not include the reference citation at the end of the replies.
              """
        )
        print(run)

        flag = True
        while flag:
            retrieved_run = client.beta.threads.runs.retrieve(
                thread_id=thread.id,
                run_id=run.id
            )
            print(f"run status --> {retrieved_run.status}")
            if retrieved_run.status == "completed":
                flag = False
        retrieved_messages = client.beta.threads.messages.list(thread_id=thread.id)
        return retrieved_messages.data[0].content[0].text.value
    except:
        return config.ERROR_MESSAGE
