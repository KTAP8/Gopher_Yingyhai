import streamlit as st
from datasets import Dataset
from sklearn.model_selection import train_test_split 
from transformers import AutoTokenizer, AutoModelForSequenceClassification, Trainer, TrainingArguments
import torch

def predict(text):
    mapped = ['Sciences','Health and Medicine','Engineering and Technology','Arts and Social Sciences and Humanities','Mathematics and Multidisciplinary','Economic and Business and Finance']
    torch.cuda.empty_cache()
    # Path to the results folder
    model_path = "./result/checkpoint-final"

    # Load the trained model
    model = AutoModelForSequenceClassification.from_pretrained(model_path)

    # Load the tokenizer
    tokenizer = AutoTokenizer.from_pretrained(model_path)

    # Move the model to the appropriate device (GPU if available, else CPU)
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    model.to(device)
    # Tokenize the input text
    inputs = tokenizer(
        [text],
        truncation=True,               # Truncate inputs longer than max_length
        padding="max_length",          # Pad inputs shorter than max_length
        max_length=512,                # Ensure compatibility with the trained model
        return_tensors="pt"            # Return PyTorch tensors
    )

    # Move inputs to the same device as the model
    inputs = {key: value.to(device) for key, value in inputs.items()}
    # Perform inference
    model.eval()
    with torch.no_grad():
        outputs = model(**inputs)
        logits = outputs.logits
        predicted_labels = torch.argmax(logits, dim=-1).tolist()
    

    print("Predicted Labels:", mapped[int(predicted_labels[0])])

# Title and subheading
st.title("Machine Learning Module")
st.subheader("Predict Subject Area from Abstract")

# Layout: Text box with submit button next to it
col1, col2 = st.columns([3, 1])  # Wider column for the text box

with col1:
    # Expanding text box
    abstract_text = st.text_area(
        "Enter the abstract below:",
        height=150,
        help="The text box will expand as you type more content."
    )

with col2:
    # Submit button
    submit = st.button("Submit")

# Placeholder for results
result_placeholder = st.empty()

# Function call and loading animation
if submit:
    if abstract_text.strip():
        with st.spinner("Predicting..."):
            # Call your predict function here
            result = predict(abstract_text)  # Assume predict is defined elsewhere
        # Display the result
        result_placeholder.markdown(f"### Prediction: {result}")
    else:
        st.error("Please enter an abstract before submitting!")



