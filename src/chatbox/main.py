def generate_response(user_input):
    return ""

def chatbot():
    print("Enter stuff here")
    while True:
        user_input = input("You: ")
        response = generate_response(user_input)
        print("Chatbot: " + response)

    
if __name__ == "__main__":
    chatbot()