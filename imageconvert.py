import os
import cv2

def convert_images_to_png(directory):
    # 画像のカウント用のインデックス
    index = 1
    
    # 指定されたディレクトリ内のファイルをリストアップ
    for filename in os.listdir(directory):
        # フルパスを取得
        file_path = os.path.join(directory, filename)
        
        # ファイルが画像であれば読み込み
        if filename.lower().endswith(('.jpg', '.jpeg', '.png', '.bmp', '.tiff')):
            # 画像を読み込む
            image = cv2.imread(file_path)

            # 新しいファイル名を作成（例: 'defect_001.png', 'defect_002.png', ...）
            new_filename = f"defect_{index:03d}.png"
            new_file_path = os.path.join(directory, new_filename)

            # 画像をPNGとして保存
            cv2.imwrite(new_file_path, image)

            # 元ファイルがPNG以外の場合は削除
            if not filename.lower().endswith('.png'):
                os.remove(file_path)

            # カウントを増やす
            index += 1

# defectsディレクトリのパスを指定
directory_path = './defects'

# 変換スクリプトを実行
convert_images_to_png(directory_path)
