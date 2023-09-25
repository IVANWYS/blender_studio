from googletrans import Translator

def trans_SC(text):
    translator = Translator()
    text = translator.translate(text, src='en', dest='zh-cn').text

    replace_SC = {"搅拌机": "Blender", "紫外线": "UV", "重量画": "权重绘制", 
                  "重量": "权重", "绘画": "绘制", "涂料表": "动画摄影表",
                  "阴影": "着色", "索具": "绑定", "骨层": "骨骼层", 
                  "油性铅笔": "蜡笔", "掩蔽": "遮罩", "{附件": "{attachment ", }
    
    for key, value in replace_SC.items():
        text = text.replace(key, value)
        
    return text

def trans_TC(text):
    translator = Translator()
    text = translator.translate(text, src='en', dest='zh-tw').text

    replace_TC = {"攪拌機": "Blender", "紫外線": "UV", "重量畫": "權重繪製", 
                  "重量": "權重", "繪畫": "繪製", "塗料表": "動畫攝影表", 
                  "陰影": "著色", "索具": "綁定", "骨層": "骨骼層", 
                  "油性鉛筆": "蠟筆", "掩蔽": "遮罩", "{附件": "{attachment ", }
    
    for key, value in replace_TC.items():
        text = text.replace(key, value)
        
    return text