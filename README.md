# myPMO Agent

**Google Chat × Gemini 3.0 Pro × Google Sheets** による影のPMOアシスタント

## 概要

15社のベンダー管理とSIT準備調整を支援するAI PMOシステム。Google Chatから質問すると、Gemini 3.0 ProがGoogle Sheetsのプロジェクトデータを参照し、PMBOKベースの分析・提案を返します。

## 主な機能

- `/ask [質問]` - Sheetsデータを参照して回答
- `/update-issue [内容]` - Issue Logに自動追記  
- `/risk-alert` - 期限超過・停滞タスクを検出

## アーキテクチャ

```
Google Chat → Cloud Functions → Gemini 3.0 Pro
                ↓
         Google Sheets (Issue Log / Schedule)
```

## セットアップ

### 1. 環境構築

```bash
# 依存関係インストール
pip install -r requirements.txt

# 環境変数設定
cp .env.example .env
# .env を編集してGCPプロジェクトID、スプレッドシートIDを設定
```

### 2. Google Sheetsの準備

**必須カラム（改善版）**:

**Issue Log**:
- ID, 起票日, カテゴリ, 内容, **ベンダー名**, 担当者, **優先度**, **期限**, ステータス, **影響範囲**, 更新日

**Schedule**:
- **ID**, タスク, **ベンダー名**, **担当者**, 開始予定, 終了予定, **ステータス**, 進捗率, メモ

詳細: `resources/knowledge/sheet_structure_proposal.md` 参照

### 3. ローカルテスト

```bash
# Sheets API接続確認
python tests/test_sheets_client.py

# Gemini API動作確認
python tests/test_gemini_client.py

# ローカルサーバー起動
functions-framework --target=handle_chat_message --debug
```

### 4. Cloud Functionsデプロイ

```bash
# デプロイ実行
bash deploy.sh

# Budget Alert設定
bash setup_budget_alert.sh
```

## コスト

**完全無料枠運用**: $0/月

- Cloud Functions: 200万リクエスト/月（無料枠）
- Gemini 3.0 Pro: 250リクエスト/日（無料枠）
- Budget Alert（$1超過時自動停止）

## ディレクトリ構造

```
my-pmo-agent/
├── config/                    # サービスアカウント鍵
├── src/
│   ├── brain/                 # Gemini AI統合
│   │   └── gemini_client.py
│   ├── tools/                 # Sheets連携・Budget監視
│   │   ├── sheets_client.py
│   │   └── budget_monitor.py
│   └── main.py                # Cloud Functions エントリーポイント
├── resources/
│   ├── knowledge/             # PMO Persona, シート構造
│   └── templates/             # レスポンステンプレート
├── tests/                     # テストコード
├── .env                       # 環境変数（Git管理外）
├── requirements.txt           # 依存関係
└── deploy.sh                  # デプロイスクリプト
```

## トラブルシューティング

### Gemini APIエラー
- レート制限（250req/日）超過 → 翌日0時（太平洋時間）にリセット
- モデル名確認: `gemini-3.0-pro-preview-1118`

### Sheets API認証エラー
- サービスアカウントにスプレッドシートの閲覧・編集権限を付与
- `SERVICE_ACCOUNT_KEY_PATH` のパス確認

## 開発者

システム構築: Gemini Antigravity AI  
PMO設計: PMBOK準拠ベストプラクティス
