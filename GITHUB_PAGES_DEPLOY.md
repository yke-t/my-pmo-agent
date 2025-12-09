# GitHub Pagesデプロイ手順

## 🚀 簡単3ステップでデプロイ

### ステップ1: Gitリポジトリ初期化（まだの場合）

```bash
cd C:\Users\yke\Projects\my-pmo-agent

# Gitリポジトリ初期化
git init

# 全てのファイルをステージング
git add .

# 初回コミット
git commit -m "Add myPMO Agent with Web Dashboard"
```

---

### ステップ2: GitHubリポジトリ作成

1. **GitHub（https://github.com）にログイン**

2. 右上の **「+」** → **「New repository」** をクリック

3. リポジトリ設定:
   - **Repository name**: `my-pmo-agent`
   - **Description**: `AI-Powered PMO Assistant`
   - **Public** を選択（無料）
   - **Initialize this repository with a README**: チェックしない

4. **「Create repository」** をクリック

5. 表示された画面で、**「...or push an existing repository from the command line」** のコマンドをコピー

---

### ステップ3: GitHubにプッシュ

```bash
# リモートリポジトリを追加（<your-username>を自分のGitHubユーザー名に変更）
git remote add origin https://github.com/<your-username>/my-pmo-agent.git

# メインブランチ名を設定
git branch -M main

# プッシュ
git push -u origin main
```

---

### ステップ4: GitHub Pages有効化

1. GitHubリポジトリページで **「Settings」** タブをクリック

2. 左メニューの **「Pages」** をクリック

3. **Source** セクション:
   - Branch: **main** を選択
   - Folder: **/docs** を選択
   - **Save** をクリック

4. 数分待つ

5. ページ上部に **「Your site is live at https://<your-username>.github.io/my-pmo-agent/」** と表示される

---

## ✅ 確認

ブラウザで以下にアクセス:
```
https://<your-username>.github.io/my-pmo-agent/
```

ダッシュボードが表示されれば成功です！

---

## 🔧 後で更新する場合

```bash
# 変更をコミット
git add .
git commit -m "Update dashboard"
git push
```

数分後に自動的にGitHub Pagesに反映されます。

---

## 💡 ヒント

- **プライベートリポジトリも可能**（GitHub Pro必要）
- **カスタムドメイン**も設定可能
- **HTTPS**: GitHub Pagesは自動的にHTTPS対応
