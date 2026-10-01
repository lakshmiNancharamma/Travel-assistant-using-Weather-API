from agent import ask_agent


print("=" * 60)
print("TRAVEL ASSISTANT")
print("=" * 60)

while True:

    question = input("\nAsk the question: ")

    if question.lower() == "exit":
        print("Goodbye!")
        break

    answer = ask_agent(question)

    print("\nAssistant:")
    print(answer)