import openai

api_key = "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"

try:
    client = openai.OpenAI(api_key=api_key)
    response = client.chat.completions.create(
        model="gpt-4",
        messages=[{"role": "system", "content": "Test API connection."}],
        max_tokens=10
    )
    print("✅ API Connection Successful:", response.choices[0].message.content)
except Exception as e:
    print("❌ API Error:", str(e))
