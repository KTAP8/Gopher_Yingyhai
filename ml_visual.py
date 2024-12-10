import streamlit as st
from datasets import Dataset
from sklearn.model_selection import train_test_split 
from transformers import AutoTokenizer, AutoModelForSequenceClassification, Trainer, TrainingArguments
import torch

from transformers import AutoTokenizer, AutoModelForSequenceClassification
import torch

def predict(text):
    # Label mapping for predictions
    mapped = [
        'Sciences',
        'Health and Medicine',
        'Engineering and Technology',
        'Arts and Social Sciences and Humanities',
        'Mathematics and Multidisciplinary',
        'Economic and Business and Finance'
    ]
    
    # Clear GPU cache
    torch.cuda.empty_cache()
    
    # Use the Hugging Face model directly
    model_name = "KTAP8/GopherSubjectArea"

    # Load the pre-trained model from Hugging Face
    model = AutoModelForSequenceClassification.from_pretrained(model_name)

    # Load the tokenizer from Hugging Face
    tokenizer = AutoTokenizer.from_pretrained(model_name)

    # Determine the device to use (GPU if available, otherwise CPU)
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

    # Map predicted label index to the corresponding label
    return mapped[int(predicted_labels[0])]


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


metrics = {
    'eval_accuracy': 0.8483373884833739,
    'eval_f1': 0.8484789634216419,
    'eval_precision': 0.8486998899398802,
    'eval_recall': 0.8483373884833739
}


# Prepare metrics for table display
formatted_metrics = [
    {"Metric": metric, "Value (%)": f"{value * 100:.2f}"}
    for metric, value in metrics.items()
]

# Display metrics as a table
st.subheader("Evaluation Metrics (model performance)")
st.table(formatted_metrics)

# Generalized fields data
generalized_fields = {
    "Sciences": [
        "AGRI",  # Agricultural and Biological Sciences
        "BIOC",  # Biochemistry, Genetics and Molecular Biology
        "EART",  # Earth and Planetary Sciences
        "ENVI",  # Environmental Science
        "MATE",  # Materials Science
        "PHYS",  # Physics and Astronomy
        "CHEM"   # Chemistry
    ],
    "Health and Medicine": [
        "DENT",  # Dentistry
        "HEAL",  # Health Professions
        "IMMU",  # Immunology and Microbiology
        "MEDI",  # Medicine
        "NEUR",  # Neuroscience
        "NURS",  # Nursing
        "PHAR",  # Pharmacology, Toxicology and Pharmaceutics
        "VETE"   # Veterinary
    ],
    "Engineering and Technology": [
        "CENG",  # Chemical Engineering
        "COMP",  # Computer Science
        "ENER",  # Energy
        "ENGI"   # Engineering
    ],
    "Arts and Social Sciences and Humanities": [
        "ARTS",  # Arts and Humanities
        "DECI",  # Decision Sciences
        "PSYC",  # Psychology
        "SOCI"   # Social Sciences
    ],
    "Mathematics and Multidisciplinary": [
        "MATH",  # Mathematics
        "MULT"   # Multidisciplinary
    ],
    "Economic and Business and Finance": [
        "BUSI",  # Business, Management and Accounting
        "ECON",  # Economics, Econometrics and Finance
    ]
}

# Add an expander for the generalized field guide
with st.expander("Generalized Field Guide"):
    st.write("Below is the mapping of generalized fields to their respective subfields:")
    for field, subfields in generalized_fields.items():
        st.markdown(f"**{field}:**")
        for subfield in subfields:
            st.write(f"- {subfield}")
