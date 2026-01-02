import streamlit as st
import torch
import torch.nn as nn
from torchvision import models, transforms
from PIL import Image

# -------- Model Load --------
@st.cache_resource
def load_model():
    model = models.resnet50(pretrained=False)
    model.fc = nn.Sequential(
        nn.Dropout(0.5),
        nn.Linear(model.fc.in_features, 128),
        nn.ReLU(),
        nn.Dropout(0.25),
        nn.Linear(128, 4)
    )
    model.load_state_dict(torch.load("tumor_resnet50.pth", map_location="cpu"))
    model.eval()
    return model

model = load_model()

# -------- Image Transform --------
transform = transforms.Compose([
    transforms.Resize((224, 224)),
    transforms.ToTensor(),
    transforms.Normalize(
        mean=[0.485, 0.456, 0.406],
        std=[0.229, 0.224, 0.225]
    )
])

class_names = ['glioma', 'meningioma', 'notumor', 'pituitary']

# -------- UI --------
st.title("🧠 Brain Tumor Detection")
st.write("Upload MRI image to predict tumor type")

uploaded_file = st.file_uploader(
    "Upload MRI Image",
    type=["jpg", "jpeg", "png"]
)

if uploaded_file:
    image = Image.open(uploaded_file).convert("RGB")
    st.image(image, caption="Uploaded Image", use_column_width=True)

    img = transform(image).unsqueeze(0)

    with torch.no_grad():
        outputs = model(img)
        probs = torch.softmax(outputs, dim=1)
        confidence, pred = torch.max(probs, 1)

    st.success(f"Prediction : **{class_names[pred.item()]}**")
    st.info(f"Confidence : **{confidence.item()*100:.2f}%**")
