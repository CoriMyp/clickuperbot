import openai

import config


openai_client = openai.OpenAI(api_key=config.OPENAI_API_KEY)

OPENAI_MODEL = "gpt-4o-mini"
SYSTEM = open("system.txt", "r").read()


def get_response(text):
	messages = [
		{ "role": "developer", "content": SYSTEM },
		{ "role": "user", "content": text }
	]
	response = send_openai(messages)
	return response


def send_openai(messages):
	try:
		response = openai_client.chat.completions.create(
			model=OPENAI_MODEL,
			messages=messages,
		)
	except openai.APIError as e:
		raise Exception(f"[OPENAI {e.code}] API Error: {e.message}")
	except openai.APIConnectionError as e:
		raise Exception(f"[OPENAI {e.code}] Failed to connect: {e.message}")
	except openai.RateLimitError as e:
		raise Exception(f"[OPENAI {e.code}] API request exceeded rate limit: {e.message}")

	return response.choices[0].message.content

