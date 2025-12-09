# Google Cloud SDK セットアップガイド

## 📦 Google Cloud SDKインストール

### Windows環境でのインストール

1. **[Google Cloud SDK インストーラー](https://cloud.google.com/sdk/docs/install)** をダウンロード

2. インストーラーを実行（`GoogleCloudSDKInstaller.exe`）

3. インストール時のオプション:
   - ✅ すべてのコンポーネントをインストール
   - ✅ Cloud SDK Shellを起動

4. インストール完了後、PowerShellを**再起動**

---

## 🔑 認証設定

### 1. Google Cloudにログイン

```powershell
gcloud auth login
```

ブラウザが開くので、Googleアカウントでログイン

### 2. プロジェクトを設定

```powershell
gcloud config set project my-pmo-agent-v1
```

### 3. アプリケーションデフォルト認証

```powershell
gcloud auth application-default login
```

---

## ✅ 確認

```powershell
# gcloudバージョン確認
gcloud version

# 現在のプロジェクト確認
gcloud config get-value project

# 認証状態確認
gcloud auth list
```

---

## 🚀 デプロイ実行

セットアップ完了後、デプロイスクリプトを実行:

```powershell
cd C:\Users\yke\Projects\my-pmo-agent
.\deploy.ps1
```

---

## 🔍 トラブルシューティング

### エラー: "gcloud: command not found"

**原因**: PATHが正しく設定されていない

**解決策**:
1. PowerShellを管理者として再起動
2. 以下のコマンドでPATHを確認:
   ```powershell
   $env:PATH
   ```
3. Google Cloud SDKのパスが含まれているか確認
   通常の場所: `C:\Users\<ユーザー名>\AppData\Local\Google\Cloud SDK\google-cloud-sdk\bin`

### エラー: "Project not found"

**原因**: プロジェクトIDが間違っているか、権限がない

**解決策**:
```powershell
# プロジェクトリストを確認
gcloud projects list

# 正しいプロジェクトIDを設定
gcloud config set project <正しいプロジェクトID>
```

### エラー: "Billing account required"

**原因**: プロジェクトに請求先アカウントがリンクされていない

**解決策**:
1. [Google Cloud Console](https://console.cloud.google.com/billing) を開く
2. プロジェクトに請求先アカウントをリンク
