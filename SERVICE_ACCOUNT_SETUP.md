# サービスアカウント認証セットアップガイド

## 🔐 ステップ1: サービスアカウント権限付与（1分）

### サービスアカウントのメールアドレス

```
pmo-agent-sa@my-pmo-agent-v1.iam.gserviceaccount.com
```

### 手順

1. **[スプレッドシートを開く](https://docs.google.com/spreadsheets/d/1C6ua596iFVCG2fx6YnYviqthrF3K4EYYxUPJhNUUt7A/edit)**

2. 右上の **「共有」** ボタンをクリック

3. 以下のメールアドレスを入力:
   ```
   pmo-agent-sa@my-pmo-agent-v1.iam.gserviceaccount.com
   ```

4. 権限を **「編集者」** に設定

5. **「通知しない」** を選択（サービスアカウントなのでメール不要）

6. **「送信」** をクリック

---

## 🚀 ステップ2: スプレッドシート構造の自動セットアップ

### 実行コマンド

```bash
cd C:\Users\yke\Projects\my-pmo-agent
python scripts/setup_sheets_structure.py
```

### 実行内容

スクリプトが自動的に以下を実行します:

1. **Issueシート**:
   - カラム追加: ベンダー名, 優先度, 期限, 影響範囲, 更新日
   - プルダウン設定: 優先度（緊急/高/中/低）、影響範囲（全体/特定ベンダー/限定的）

2. **Scheduleシート**:
   - カラム追加: ID（先頭）, ベンダー名, 担当者, ステータス
   - プルダウン設定: ステータス（未着手/進行中/停滞/完了/保留）

---

## ✅ 完了確認

スクリプト実行後、以下を確認してください:

1. スプレッドシートを開いて、新しいカラムが追加されていることを確認
2. プルダウンメニューが正しく設定されていることを確認

---

## 🔍 トラブルシューティング

### エラー: "Permission denied"

**原因**: サービスアカウントに編集権限が付与されていない

**解決策**: ステップ1を再確認し、サービスアカウントに「編集者」権限を付与

### エラー: "Spreadsheet not found"

**原因**: `.env`ファイルのSPREADSHEET_IDが正しくない

**解決策**: `.env`ファイルを確認:
```
SPREADSHEET_ID=1C6ua596iFVCG2fx6YnYviqthrF3K4EYYxUPJhNUUt7A
```
