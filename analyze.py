#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Jun 12 19:53:26 2024

@author: yashbagia
"""


import os
import shutil
from PIL import Image
import torch
import torchvision.transforms as transforms
import torchvision.models as models
import numpy as np
import openai
from transformers import AutoTokenizer, AutoModel

openai.api_key = os.getenv('OPENAI_API_KEY', 'sk-proj-7rOXHmNuLjMRmxKKyA3uT3BlbkFJsStdreVgE5nM87hGM0u4')

image_model = models.resnet50(weights=True)
image_model.eval()

tokenizer = AutoTokenizer.from_pretrained('sentence-transformers/all-MiniLM-L6-v2')
text_model = AutoModel.from_pretrained('sentence-transformers/all-MiniLM-L6-v2')

transform = transforms.Compose([
    transforms.Resize((224, 224)),
    transforms.ToTensor(),
    transforms.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225]),
])

def get_image_embedding(image_path):
    image = Image.open(image_path).convert('RGB')
    image = transform(image).unsqueeze(0)
    with torch.no_grad():
        embedding = image_model(image).squeeze().numpy()
    return embedding

def get_image_description(image_path):
    prompt = f"Describe the contents of the image at {image_path}."
    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[{"role": "system", "content": prompt}]
    )
    return response.choices[0].message['content']

def get_text_embedding(text):
    inputs = tokenizer(text, return_tensors='pt', truncation=True, padding=True)
    with torch.no_grad():
        outputs = text_model(**inputs)
    return outputs.last_hidden_state.mean(dim=1).squeeze().numpy()

def cosine_similarity(vec1, vec2):
    return np.dot(vec1, vec2) / (np.linalg.norm(vec1) * np.linalg.norm(vec2))

def analyze_images(output_directory, sorted_directory):
    os.makedirs(sorted_directory, exist_ok=True)
    combined_embeddings = []

    for filename in os.listdir(output_directory):
        if filename.endswith(".png"):
            image_path = os.path.join(output_directory, filename)
            img_embedding = get_image_embedding(image_path)
            img_description = get_image_description(image_path)
            text_embedding = get_text_embedding(img_description)
            combined_embedding = np.concatenate((img_embedding, text_embedding))
            combined_embeddings.append((filename, combined_embedding))

    def copy_image_to_folder(src_image, dst_image, similarity, src_folder, dst_folder):
        if similarity >= 85:
            target_folder = os.path.join(dst_folder, 'above_70')
        else:
            target_folder = os.path.join(dst_folder, 'below_70')
        os.makedirs(target_folder, exist_ok=True)
        shutil.copy(os.path.join(src_folder, dst_image), target_folder)

    for i in range(len(combined_embeddings)):
        file1, embedding1 = combined_embeddings[i]
        screen_folder = os.path.join(sorted_directory, f'screen_{i+1}')
        os.makedirs(screen_folder, exist_ok=True)

        for j in range(len(combined_embeddings)):
            if i != j:
                file2, embedding2 = combined_embeddings[j]
                similarity = cosine_similarity(embedding1, embedding2)
                similarity_percentage = similarity * 100
                copy_image_to_folder(file1, file2, similarity_percentage, output_directory, screen_folder)
                print(f"Similarity between {file1} and {file2}: {similarity_percentage:.2f}%")

def clear_sorted_images():
    sorted_images_path = os.path.join('static', 'sorted_images')
    if os.path.exists(sorted_images_path):
        shutil.rmtree(sorted_images_path)
    os.makedirs(sorted_images_path, exist_ok=True)

def trigger_analysis():
    clear_sorted_images()
    analyze_images('static/output_images', 'static/sorted_images')

if __name__ == '__main__':
    trigger_analysis()
