# Dummy inference file required for submission

def predict(input_data):
    return {
        "message": "OpenEnv GridWorld is running successfully",
        "input": input_data
    }

if __name__ == "__main__":
    print(predict({"status": "ok"}))
