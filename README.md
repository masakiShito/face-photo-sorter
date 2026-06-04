# face-photo-sorter

PC内に保存された写真フォルダから、特定人物が写っている可能性が高い画像を顔認識で抽出・分類するローカルアプリです。

対象人物のサンプル写真フォルダと照合し、結果に応じて `matched` / `unmatched` / `unknown` フォルダへ写真をコピーします。写真データは外部サーバーへ送信せず、すべてローカルPC上で処理します。

## 主な機能

* Streamlitによる簡易GUI
* 解析対象フォルダの再帰スキャン
* `.jpg` / `.jpeg` / `.png` / `.webp` の読み込み
* DeepFaceによる対象人物サンプル写真との照合
* `matched` / `unmatched` / `unknown` へのコピー分類
* 同名ファイルの上書き防止
* 解析件数、分類件数、エラー件数、進捗、最終結果一覧の表示
* 1枚の写真でエラーが出ても処理を継続

## 技術スタック

* Python
* Streamlit
* DeepFace
* OpenCV
* Pillow
* NumPy
* pandas
* pathlib
* shutil

SQLiteは初期MVPでは未使用ですが、解析履歴やキャッシュ保存を追加しやすい構成にしています。

## セットアップ手順

### 1. 仮想環境の作成

```bash
python -m venv .venv
```

### 2. 仮想環境の有効化

macOS / Linux:

```bash
source .venv/bin/activate
```

Windows PowerShell:

```powershell
.venv\Scripts\Activate.ps1
```

### 3. 依存関係のインストール

```bash
pip install -r requirements.txt
```

DeepFaceは初回実行時にモデルファイルをローカルへダウンロードする場合があります。以降の顔認識処理自体はローカルで実行されます。

## 起動方法

```bash
streamlit run app/main.py
```

## 使い方

1. 対象人物のサンプル写真を任意のフォルダに用意します。
2. 分類したい写真が入ったフォルダを用意します。
3. アプリを起動します。
4. 画面左側で以下を指定します。
   * 解析対象の写真フォルダ
   * 対象人物のサンプル写真フォルダ
   * 出力フォルダ
   * 類似度判定のしきい値
5. 「スキャン開始」を押します。
6. 出力フォルダ配下に分類結果がコピーされます。

出力例:

```txt
photos/output/
  matched/
  unmatched/
  unknown/
```

## 分類ルール

* `matched`: 対象人物が写っている可能性が高い写真
* `unmatched`: 対象人物とは一致しないと判定された写真
* `unknown`: 顔が検出できない、サンプルが無効、照合に失敗したなど判定不能な写真

しきい値はDeepFaceのdistanceに対する値です。distanceは小さいほど似ています。このアプリでは、distanceがしきい値以下の場合に `matched` とします。

## ディレクトリ構成

```txt
face-photo-sorter/
  app/
    __init__.py
    main.py
    config.py

    services/
      __init__.py
      face_service.py
      photo_service.py
      file_service.py

    models/
      __init__.py
      scan_result.py

    utils/
      __init__.py
      logger.py

  photos/
    input/
    target/
    output/
      matched/
      unmatched/
      unknown/

  data/

  README.md
  .gitignore
  requirements.txt
```

## 注意事項

* 元写真は削除しません。
* 元写真は移動しません。初期MVPではコピーのみ対応しています。
* 顔認識には誤判定があります。`matched` の結果も必ず目視確認してください。
* 顔が横向き、暗い、ぼけている、マスクやサングラスがある場合は判定精度が下がります。
* 写真データはGit管理しないでください。
* `photos/input/`、`photos/target/`、`photos/output/`、`data/` は `.gitignore` で除外しています。
* HEIC形式はMVPでは対象外です。今後対応予定です。
* 外部APIやクラウドサービスは使用しません。

## 今後の拡張予定

* HEIC形式への対応
* 複数人物の登録と人物別フォルダ分類
* SQLiteによる解析履歴の保存
* 顔特徴量のキャッシュ化による大量写真の高速化
* 判定結果の手動修正UI
* 年月別、イベント別の追加分類
* 類似画像、重複写真の検出
* 移動モードの追加。ただし安全確認を必須にする予定です。
