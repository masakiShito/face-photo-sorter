# face-photo-sorter

PC内に保存された写真から、特定人物が写っている画像を顔認識で抽出・分類するローカルアプリです。

家族写真や子どもの成長記録など、大量の写真の中から「特定の人物が写っている写真だけを取り出したい」という用途を想定しています。

## 概要

`family-face-sorter` は、対象人物のサンプル写真をもとに、PC内の写真フォルダをスキャンし、対象人物が写っている可能性の高い写真を抽出します。

初期バージョンでは、誤判定による元写真の紛失を防ぐため、写真の「移動」ではなく「コピー」による分類を基本とします。

## 主な機能

* 対象人物のサンプル写真を登録
* PC内の写真フォルダをスキャン
* 顔認識による人物判定
* 対象人物が写っている写真を専用フォルダへコピー
* 判定結果のログ出力
* 顔が検出できなかった写真の分類
* 将来的にはGUIによる操作に対応予定

## 想定ユースケース

* 子どもの写真だけを抽出したい
* 家族写真を人物ごとに整理したい
* 大量のスマホ写真をPC上で分類したい
* NASや外付けSSDに保存する前に写真を整理したい

## 技術スタック

初期開発では、以下の技術を使用する予定です。

* Python
* DeepFace
* OpenCV
* Pillow
* Streamlit
* SQLite
* pathlib
* shutil

## ディレクトリ構成案

```txt
family-face-sorter/
  app/
    main.py
    config.py

    services/
      face_service.py
      photo_service.py
      file_service.py

    repositories/
      photo_repository.py

    models/
      photo.py
      person.py
      scan_result.py

    utils/
      image_loader.py
      logger.py

  data/
    app.db

  photos/
    input/
    target/
    output/
      matched/
      unmatched/
      unknown/

  README.md
  .gitignore
  requirements.txt
```

## MVPで実装する機能

最初のMVPでは、以下の流れで動作することを目標にします。

1. 対象人物のサンプル写真を `photos/target/` に配置する
2. 分類したい写真を `photos/input/` に配置する
3. スクリプトを実行する
4. 対象人物が写っていると判定された写真を `photos/output/matched/` にコピーする
5. 判定できなかった写真を `photos/output/unknown/` にコピーする

## 今後の拡張予定

* Streamlitによる簡易GUI化
* 複数人物の登録
* 人物ごとの自動分類
* HEIC形式への対応
* EXIF情報をもとにした年月別フォルダ整理
* 重複写真の検出
* 類似度スコアの表示
* 判定結果の手動修正
* SQLiteによる解析履歴の保存
* 移動モードの追加

## 注意事項

このアプリはローカル環境での利用を前提としています。

顔写真や家族写真など、プライバシー性の高いデータを扱うため、写真データを外部サーバーへ送信しない設計を基本方針とします。

また、顔認識には誤判定が発生する可能性があります。初期バージョンでは、元写真を直接移動・削除せず、コピーによる分類を推奨します。

## 開発方針

* まずは小さく動くMVPを作る
* 元写真を破壊しない安全な設計にする
* ローカル完結を優先する
* 後からGUI化しやすい構成にする
* 家族写真の整理に実用できるレベルを目指す

## ライセンス

未定
