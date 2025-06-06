# -*- coding: utf-8 -*-
"""project2.ipynb

Automatically generated by Colab.

Original file is located at
    https://colab.research.google.com/drive/1kivSr1O88CXmhOtEqo408-5yuhEo3cEW
"""

from google.colab import drive
drive.mount('/content/drive')

import os
root_dir = "/content/drive/MyDrive/Colab Notebooks/ml/project"
os.chdir(root_dir)
os.listdir()

# 如果你在本地端執行，可取消註解以下指令安裝
!pip install torch torchvision

import torch
import torch.nn as nn
import torch.optim as optim
from torchvision import transforms, models
from PIL import Image
import os
from tqdm import tqdm
import matplotlib.pyplot as plt

device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
print("使用設備：", device)

# 圖片轉 tensor 的工具
loader = transforms.Compose([
    transforms.Resize((512, 512)), # 將圖片調整成 512x512
    transforms.ToTensor()
])

# tensor 轉圖片
unloader = transforms.ToPILImage()

# 讀圖 & 預處理
def image_loader(image_name):
    image = Image.open(image_name).convert("RGB")
    image = loader(image).unsqueeze(0)
    return image.to(device, torch.float)

# 損失計算工具
class ContentLoss(nn.Module):
    def __init__(self, target):
        super(ContentLoss, self).__init__()
        self.target = target.detach()
    def forward(self, x):
        self.loss = nn.functional.mse_loss(x, self.target)
        return x

def gram_matrix(input):
    b, c, h, w = input.size()
    features = input.view(b * c, h * w)
    G = torch.mm(features, features.t())
    return G.div(b * c * h * w)

class StyleLoss(nn.Module):
    def __init__(self, target_feature):
        super(StyleLoss, self).__init__()
        self.target = gram_matrix(target_feature).detach()
    def forward(self, x):
        G = gram_matrix(x)
        self.loss = nn.functional.mse_loss(G, self.target)
        return x

# 建構VGG19 + 插入 ContentLoss 與 StyleLoss 層模型，加入損失層
def get_style_model_and_losses(cnn, style_img, content_img):
    cnn = cnn.to(device).eval()
    # 指定哪些層作為 content 與 style 的特徵提取層
    content_layers = ['conv_4']
    style_layers = ['conv_1', 'conv_2', 'conv_3', 'conv_4', 'conv_5']

    content_losses = []
    style_losses = []

    model = nn.Sequential().to(device)  # 建立新的模型
    i = 0
    for layer in cnn.children():
        if isinstance(layer, nn.Conv2d):
            i += 1
            name = f"conv_{i}"
        elif isinstance(layer, nn.ReLU):
            name = f"relu_{i}"
            layer = nn.ReLU(inplace=False)
        elif isinstance(layer, nn.MaxPool2d):
            name = f"pool_{i}"
        elif isinstance(layer, nn.BatchNorm2d):
            name = f"bn_{i}"
        else:
            continue

        model.add_module(name, layer)

        if name in content_layers:
            target = model(content_img).detach()
            content_loss = ContentLoss(target)
            model.add_module("content_loss_{}".format(i), content_loss)
            content_losses.append(content_loss)

        if name in style_layers:
            target_feature = model(style_img).detach()
            style_loss = StyleLoss(target_feature)
            model.add_module("style_loss_{}".format(i), style_loss)
            style_losses.append(style_loss)

    # 擷取到最後一層損失的位置即可
    for i in range(len(model) - 1, -1, -1):
        if isinstance(model[i], (ContentLoss, StyleLoss)):
            break
    model = model[:i+1]

    return model, style_losses, content_losses

# 優化迴圈
def run_style_transfer(cnn, content_img, style_img, num_steps=300, style_weight=1e6, content_weight=1):
    input_img = content_img.clone()
    model, style_losses, content_losses = get_style_model_and_losses(cnn, style_img, content_img)
    optimizer = optim.LBFGS([input_img.requires_grad_()])

    run = [0]
    while run[0] <= num_steps:
        def closure():
            input_img.data.clamp_(0, 1)
            optimizer.zero_grad()
            model(input_img)
            style_score = sum(sl.loss for sl in style_losses)
            content_score = sum(cl.loss for cl in content_losses)
            loss = style_weight * style_score + content_weight * content_score
            loss.backward()
            run[0] += 1
            return loss
        optimizer.step(closure)

    input_img.data.clamp_(0, 1)
    return input_img

# 圖片路徑設定
# content_dir = "/content/input_images"
content_dir = "/content/drive/MyDrive/Colab Notebooks/ml/project/input/knn-styletransfer/"
style_path = "/content/drive/MyDrive/Colab Notebooks/ml/project/input/knn-styletransfer/vangogh-style/kNNstyle.jpg"
output_dir = "./output2"
os.makedirs(output_dir, exist_ok=True)

# 載入風格圖
style_img = image_loader(style_path) #提取風格圖

# 載入 CNN 模型
cnn = models.vgg19(pretrained=True).features

# 是否顯示轉換結果（太多圖可設為 False）
show_results = True

for fname in tqdm(content_files, desc="風格轉換中"):
    content_path = os.path.join(content_dir, fname)
    content_img = image_loader(content_path) #提取內容圖

    output = run_style_transfer(cnn, content_img, style_img)

    output_img = unloader(output.squeeze(0).cpu())
    output_filename = f"output_{fname}"
    output_path = os.path.join(output_dir, output_filename)
    output_img.save(output_path)

    if show_results:
        # 顯示 input 與 output 對照
        fig, axs = plt.subplots(1, 2, figsize=(10, 5))
        axs[0].imshow(unloader(content_img.squeeze(0).cpu()))
        axs[0].set_title(f"Input: {fname}")
        axs[0].axis("off")

        axs[1].imshow(output_img)
        axs[1].set_title(f"Output: {output_filename}")
        axs[1].axis("off")

        plt.tight_layout()
        plt.show()