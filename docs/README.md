# myPMO Agent - Web Dashboard

無料で使えるWebダッシュボードです。GitHub Pagesでホスティングされています。

## 🌐 アクセス方法

**GitHub Pagesにデプロイ後**: `https://<your-username>.github.io/my-pmo-agent/`

## ✨ 機能

- **AI分析** - Gemini 2.5 FlashによるPMO分析
- **リスク検出** - 期限超過課題・停滞タスクの自動検出
- **課題追加** - Google Sheetsへの課題登録

## 🚀 ローカルでのテスト

```bash
# シンプルなHTTPサーバーを起動
cd docs
python -m http.server 8000
```

ブラウザで `http://localhost:8000` を開く

## 📦 GitHub Pagesへのデプロイ

### 1. GitHubリポジトリ作成

```bash
cd C:\Users\yke\Projects\my-pmo-agent
git init
git add .
git commit -m "Initial commit: myPMO Agent"
```

### 2. GitHubにプッシュ

```bash
# GitHubでリポジトリ作成後
git remote add origin https://github.com/<your-username>/my-pmo-agent.git
git branch -M main
git push -u origin main
```

### 3. GitHub Pages設定

1. GitHubリポジトリ → **Settings**
2. 左メニュー → **Pages**
3. Source: **Deploy from a branch**
4. Branch: **main** / **docs** フォルダ
5. **Save**

数分後、`https://<your-username>.github.io/my-pmo-agent/` でアクセス可能！

## 🔧 カスタマイズ

### API URLの変更

`docs/app.js` の `API_URL` を編集:

```javascript
const API_URL = 'https://your-cloud-functions-url';
```

## 💰 コスト

**完全無料** - GitHub Pagesは静的サイトホスティングが無料です。

## 📱 対応デバイス

- ✅ デスクトップ（Chrome, Firefox, Safari, Edge）
- ✅ タブレット（iPad, Android）
- ✅ スマートフォン（iOS, Android）

## 🔒 セキュリティ

現在、認証なしで誰でもアクセス可能です。

**本番環境での推奨事項**:
- Cloud FunctionsでCORS設定
- 基本認証の追加
- APIキー認証

## 🎨 デザイン

- モダンなフラットデザイン
- レスポンシブ対応
- Googleカラーパレット準拠

## 📚 技術スタック

- **HTML5**
- **CSS3** (Grid, Flexbox)
- **Vanilla JavaScript** (ES6+)
- **Cloud Functions** (Backend API)
- **GitHub Pages** (Hosting)
