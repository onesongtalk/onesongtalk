# 灣聲宮喂 ONESONG TALK 官網

單頁式網站，包含：首頁、四檔節目、最新集數（自動更新）、藝文合作（不顯示報價）、合作洽詢表單。

## 檔案
- `index.html`：整個網站（文字直接改這裡）
- `assets/`：logo、主持人合照
- `data/episodes.json`、`data/episodes.js`：集數資料（由腳本自動產生，不用手改）
- `scripts/update_episodes.py`：從 YouTube 四個節目播放清單抓最新完整集數
- `.github/workflows/weekly-update.yml`：每週一、四中午自動跑腳本

## 自動更新怎麼運作
腳本只收標題含「｜#節目名 EPxx」的完整集數，短影音會自動排除。
只要 YouTube 上架時維持這個標題格式，官網就會自動出現新集數，並標示 NEW。

## 上線（免費：GitHub Pages）
1. 在 GitHub 建立一個新 repo，把這個資料夾全部上傳
2. repo 的 Settings → Pages → Source 選「GitHub Actions」
3. Settings → Actions → General → Workflow permissions 勾選「Read and write」
4. Actions 分頁 → 選「每週自動更新節目集數並發布網站」→ Run workflow，第一次發布
5. 要綁自己的網域（例如 onesongtalk.com）在 Settings → Pages → Custom domain 設定

## 手動更新集數
```
python3 scripts/update_episodes.py
```

## 待補
- SoundOn / Spotify / Apple Podcasts 收聽連結（`index.html` 內搜尋 TODO）
- 四檔節目介紹文字、主持人介紹請再確認
