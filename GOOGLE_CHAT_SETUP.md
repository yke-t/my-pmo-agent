# Google Chat Webhook Setup Guide

## 🚀 ステップ1: Google Chatスペース作成

1. **[Google Chat](https://chat.google.com)** を開く

2. 左サイドバーの **「＋」** → **「スペースを作成」** をクリック

3. スペース設定:
   - 名前: `myPMO Agent`
   - 説明: `PMOアシスタント（15社ベンダー管理）`
   - アクセス: 自分のみ（テスト用）

4. **「作成」** をクリック

---

## 🔗 ステップ2: Webhook URL設定

1. 作成したスペースで、**スペース名をクリック** → **「アプリと統合」** を選択

2. **「Webhookを管理」** をクリック

3. **「Webhookを追加」** をクリック

4. Webhook設定:
   - 名前: `myPMO Agent`
   - アバターURL: (任意)
   
5. **「保存」** をクリック

6. 表示された **Webhook URL** をコピー
   ```
   例: https://chat.googleapis.com/v1/spaces/AAAA.../messages?key=...
   ```

---

## 🔧 ステップ3: Cloud Functions URL設定

### 3-1. Cloud Functions URLを取得

デプロイ後に表示されたURLをコピーします。

```bash
# または以下のコマンドで取得
gcloud functions describe my-pmo-agent --region=us-central1 --format='value(serviceConfig.uri)'
```

### 3-2. トリガーURLの設定

**重要**: 現在のデプロイではHTTPトリガーを使用していますが、Google Chat統合には追加の設定が必要です。

---

## 🎯 ステップ4: Google Chat App設定（推奨）

Google Chat Webhookではなく、**Google Chat App**として設定することをお勧めします。

### 手順

1. **[Google Cloud Console](https://console.cloud.google.com)** を開く

2. **APIs & Services** → **有効なAPIとサービス** → **Google Chat API**

3. **「構成」** タブで以下を設定:
   - アプリ名: `myPMO Agent`
   - アバターURL: (任意)
   - 説明: `PMOアシスタント`
   - 機能: ✅ 1対1のメッセージを受信する、✅ スペースとグループの会話に参加する
   - 接続設定: **Cloud Pub/Sub** または **HTTP エンドポイント**
     - HTTP エンドポイント: `<Cloud Functions URL>`
   - 表示設定: アプリをインストールできるユーザー → **特定のユーザーとグループ**

4. **「保存」** をクリック

5. スペースに戻り、**「アプリを追加」** → `myPMO Agent` を検索して追加

---

## ✅ ステップ5: 動作確認

スペースで以下のコマンドをテスト:

```
@myPMO Agent /ask 現在の課題数は？
```

期待される動作:
- AIがGoogle Sheetsを参照
- JSON形式で分析・推奨・Next Actionを返答

---

## 🔍 トラブルシューティング

### エラー: "アプリが応答しません"

**原因**: Cloud Functions URLが正しく設定されていない

**解決策**:
1. Cloud Functions URLが正しいか確認
2. Cloud Functionsが正常にデプロイされているか確認:
   ```bash
   gcloud functions describe my-pmo-agent --region=us-central1
   ```
3. ログを確認:
   ```bash
   gcloud functions logs read my-pmo-agent --region=us-central1 --limit=50
   ```

### エラー: "403 Forbidden"

**原因**: サービスアカウント権限不足

**解決策**:
1. サービスアカウントに以下の権限を付与:
   - Cloud Functions Invoker
   - Vertex AI User
   - (スプレッドシート編集権限は既に付与済み)

---

## 📌 Next Steps

動作確認が完了したら、以下を試してください:

1. **Issue追加テスト**:
   ```
   @myPMO Agent /update-issue 技術課題|API連携エラー|ベンダーA|鈴木|高|2025-12-15|全体
   ```

2. **リスク検出テスト**:
   ```
   @myPMO Agent /risk-alert
   ```

3. **PMO分析テスト**:
   ```
   @myPMO Agent /ask SIT準備の進捗状況を教えてください
   ```
