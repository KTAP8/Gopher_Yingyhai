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


predict("""Nowadays, precision agriculture combined with modern information and
communications technologies, is becoming more common in agricultural activities
such as automated irrigation systems, precision planting, variable rate
applications of nutrients and pesticides, and agricultural decision support
systems. In the latter, crop management data analysis, based on machine
learning and data mining, focuses mainly on how to efficiently forecast and
improve crop yield. In recent years, raw and semi-processed agricultural data
are usually collected using sensors, robots, satellites, weather stations, farm
equipment, farmers and agribusinesses while the Internet of Things (IoT) should
deliver the promise of wirelessly connecting objects and devices in the
agricultural ecosystem. Agricultural data typically captures information about
farming entities and operations. Every farming entity encapsulates an
individual farming concept, such as field, crop, seed, soil, temperature,
humidity, pest, and weed. Agricultural datasets are spatial, temporal, complex,
heterogeneous, non-standardized, and very large. In particular, agricultural
data is considered as Big Data in terms of volume, variety, velocity and
veracity. Designing and developing a data warehouse for precision agriculture
is a key foundation for establishing a crop intelligence platform, which will
enable resource efficient agronomy decision making and recommendations. Some of
the requirements for such an agricultural data warehouse are privacy, security,
and real-time access among its stakeholders (e.g., farmers, farm equipment
manufacturers, agribusinesses, co-operative societies, customers and possibly
Government agencies). However, currently there are very few reports in the
literature that focus on the design of efficient data warehouses with the view
of enabling Agricultural Big Data analysis and data mining.""")

