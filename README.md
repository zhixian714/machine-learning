# machine-learning
1.1 圖像風格轉換：使用預訓練卷積神經網路生成藝術風格影像   

1.2 Introduction (Motivation, Objectives):
	圖像風格轉換是一種將「內容圖」的結構與形狀，以及「風格圖」的紋理與筆觸結合，產生混合風格影像的技術。

1.2 動機:
	最近很流行吉卜力畫風，因此想寫個轉換畫風的程式，不會受限於gpt的使用限制。  
1.2.2 目的或做完此專題，要解決的問題:  
	解決被gpt限制的問題，不屈服於pro。  
1.3 Related works  
	knn，較簡單容易上手，但風格轉換較不明顯，比較像濾鏡轉換。  
1.4 My Methods  
1.4.1 使用模型  
•	使用 torchvision.models.vgg19(pretrained=True) 所載入的 VGG-19 預訓練模型。  
•	模型僅作為特徵提取器使用，不進行權重微調（fine-tuning）。  
1.4.2 特徵提取  
•	內容特徵：取自較深層（如 conv4_2），保留圖像的結構與物件輪廓。  
•	風格特徵：取自多個層（如 conv1_1, conv2_1, ..., conv5_1），並透過 Gram Matrix 表示風格（如筆觸、紋理）。  
#1.4.3 損失函數    
總損失為內容損失與風格損失的加權組合：  
•	內容損失（Content Loss）：  
用 MSE（均方誤差）計算生成圖與原始內容圖在指定層的特徵差距。  
•	風格損失（Style Loss）：  
將每一層風格特徵轉換為 Gram Matrix，與風格圖的對應層進行 MSE 計算。  
•	總損失（Total Loss）：  
Loss=α×Content Loss+β×Style Loss ,α、β 控制內容與風格的平衡。  

1.4.4 Datasets  
	真實照片（例如風景、建築）  
1.4.5 Experimental Results, and Conclusion   
	內容圖、風格圖、輸出圖  
