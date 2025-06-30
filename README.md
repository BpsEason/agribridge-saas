AgriBridge SaaS 平台[cite_start]AgriBridge 是一個模組化的農業 SaaS 平台，專為永續農業設計，旨在提升效率與透明度 [cite: 1][cite_start]。它結合了 多租戶架構、LINE Bot 通知、IoT 數據監測、區塊鏈交易追蹤 與 ESG 報表可視化，為農民與買家提供數據驅動的解決方案 [cite: 1][cite_start]。本專案僅包含核心代碼，需手動安裝外部套件，確保系統穩定、可擴展 [cite: 1]。核心功能[cite_start]多租戶 SaaS 架構：透過 tenant_id 實現數據隔離，確保農民、產品、訂單資料獨立 [cite: 1]。[cite_start]LINE Bot 整合：支援即時訂單通知，動態配置用戶 ID（開發環境模擬） [cite: 1]。[cite_start]IoT 數據監測：模擬農場感測器數據（溫度、濕度），以 Chart.js 可視化 [cite: 1]。[cite_start]區塊鏈交易追蹤：模擬交易記錄，確保供應鏈透明 [cite: 1]。[cite_start]ESG 報表可視化：計算 ESG 分數，透過前端圖表展示永續指標 [cite: 1, 5, 11]。[cite_start]CI/CD 自動化：GitHub Actions 實現測試、檢查與部署 [cite: 1, 10, 14]。[cite_start]安全認證：JWT 認證，支援租戶級別訪問控制 [cite: 1]。[cite_start]前端體驗：Vue 3 搭配 TailwindCSS，打造響應式介面 [cite: 1, 2]。[cite_start]資料庫初始化與環境變數驗證: 應用程式啟動時會檢查並插入預設數據，確保首次部署或測試環境具備最小運行條件 [cite: 15, 7][cite_start]。同時使用 pydantic_settings 驗證環境變數，防止配置錯誤 [cite: 13]。系統架構[cite_start]採用模組化設計 [cite: 1]。架構圖graph TD
    A[用戶] -->|HTTP| B[前端: Vue 3 + TailwindCSS]
    B -->|API 請求| C[後端: FastAPI]
    C -->|SQL| D[MySQL: 多租戶資料庫]
    C -->|快取| E[Redis]
    C -->|Webhook| F[LINE Bot]
    C -->|模擬數據| G[IoT 模組]
    C -->|模擬記錄| H[區塊鏈模組]
    B -->|可視化| I[Chart.js: ESG 報表]
    J[GitHub Actions] -->|CI/CD| K[Docker Hub]
    J -->|部署| L[VPS / Vercel]
[cite_start][cite: 2, 3, 4, 5, 6]元件說明前端應用 (Vue 3 + TailwindCSS)：[cite_start]負責用戶介面展示、數據可視化（透過 Chart.js 呈現 ESG 報告與 IoT 歷史數據），以及與後端 API 的交互 [cite: 5, 11]。[cite_start]使用 Pinia 進行狀態管理，並支援動態數據與圖表 [cite: 1, 1, 8]。後端 API 服務 (FastAPI)：[cite_start]基於 Python 的高效能 Web 框架，內建 Pydantic 數據驗證，自動生成 OpenAPI (Swagger) 和 ReDoc 文檔 [cite: 1, 15]。[cite_start]透過 JWT 處理身份驗證和授權，並實現多租戶數據過濾 [cite: 1, 13]。MySQL 資料庫 (8.0)：[cite_start]作為主要數據持久層，採用 tenant_id 欄位實現多租戶數據隔離 [cite: 1, 3]。Redis 快取 (7.0)：[cite_start]用於快取常用數據，提高讀取性能 [cite: 1]。LINE Bot：[cite_start]支援即時推播與 webhook [cite: 1, 1]。DevOps (Docker, GitHub Actions, Vercel)：[cite_start]所有服務容器化，確保開發、測試、部署環境的一致性 [cite: 1, 6]。3. 技術棧[cite_start]後端：FastAPI (Python 3.11) [cite: 1, 7][cite_start], SQLAlchemy [cite: 1, 7][cite_start], PyMySQL [cite: 1, 20][cite_start], Redis [cite: 1, 20][cite_start], PyJWT [cite: 1, 20][cite_start], line-bot-sdk [cite: 1, 20][cite_start], Pandas [cite: 20][cite_start], scikit-learn[cite: 20].[cite_start]前端：Vue 3 [cite: 1, 8][cite_start], Pinia [cite: 1, 8][cite_start], Vue Router [cite: 8][cite_start], Axios [cite: 8][cite_start], TailwindCSS [cite: 1, 9][cite_start], Chart.js [cite: 1, 8][cite_start], vue-toastification[cite: 8].[cite_start]資料庫：MySQL 8.0[cite: 1, 22].[cite_start]快取：Redis 7.0[cite: 1].[cite_start]容器化：Docker [cite: 1][cite_start], Docker Compose[cite: 10, 1].[cite_start]CI/CD：GitHub Actions [cite: 10][cite_start], Vercel（前端可選）[cite: 6].[cite_start]測試：Pytest [cite: 1][cite_start], Vitest [cite: 1][cite_start], Flake8 [cite: 24][cite_start], Bandit [cite: 25][cite_start], ESLint[cite: 24].[cite_start]其他：Nginx（前端生產環境）、phpMyAdmin（資料庫管理）[cite: 1].4. 專案結構agribridge-saas/
├── api/                    # FastAPI 後端
[cite_start]│   ├── routes/            # API 路由（認證、農民、產品、訂單、IoT、區塊鏈） [cite: 7]
[cite_start]│   ├── schemas/           # Pydantic 模型 [cite: 7]
[cite_start]│   ├── services/          # 業務邏輯（ESG 計算、模擬區塊鏈） [cite: 7]
[cite_start]│   ├── models.py          # SQLAlchemy ORM 模型 [cite: 7]
[cite_start]│   ├── main.py            # FastAPI 入口 [cite: 7]
[cite_start]│   ├── requirements.txt   # Python 依賴 [cite: 7]
[cite_start]│   └── Dockerfile         # 後端 Docker 配置 [cite: 7]
├── frontend/               # Vue 3 前端
[cite_start]│   ├── src/               # Vue 程式碼 [cite: 8]
[cite_start]│   │   ├── views/         # 頁面（DashboardView、LoginView） [cite: 8]
[cite_start]│   │   ├── components/    # 可重用組件 [cite: 8]
[cite_start]│   │   ├── router/        # Vue Router 配置 [cite: 8]
[cite_start]│   │   ├── stores/        # Pinia 狀態管理（認證） [cite: 8]
[cite_start]│   │   └── api/           # API 客戶端工具 [cite: 8]
[cite_start]│   ├── package.json       # Node.js 依賴 [cite: 8]
[cite_start]│   ├── vite.config.js     # Vite 配置 [cite: 9]
[cite_start]│   └── Dockerfile         # 前端 Docker 配置 [cite: 9]
[cite_start]├── notification/           # LINE Bot 服務 [cite: 10]
[cite_start]├── docs/                  # API 與架構文件 [cite: 10]
[cite_start]├── tests/                 # 測試（Pytest、Vitest） [cite: 10]
[cite_start]├── deploy/                # 部署配置 [cite: 10]
[cite_start]├── .github/workflows/     # CI/CD 流程 [cite: 10]
[cite_start]├── .env                   # 環境變數 [cite: 10]
[cite_start]├── docker-compose.yml     # Docker Compose 配置 [cite: 10]
[cite_start]├── LICENSE                # MIT 授權文件 [cite: 10]
[cite_start]└── README.md              # 專案說明 [cite: 10]
5. 問與答 (Q&A)1. 專案概述與架構[cite_start]Q: AgriBridge 的目標、主要功能和解決的痛點是什麼？ A: AgriBridge 旨在提升永續農業效率與透明度，解決資訊不對稱、供應鏈透明度不足及環境數據管理困難等痛點 [cite: 11][cite_start]。主要功能包括多租戶產品與訂單管理、LINE Bot 通知、IoT 數據監測、區塊鏈交易追蹤及 ESG 報表可視化，幫助農民優化運營，買家追蹤產品來源 [cite: 1, 11]。[cite_start]Q: AgriBridge 的整體系統架構如何？各模組如何協作？ A: 系統採用模組化架構 [cite: 1, 11][cite_start]。前端（Vue 3 + TailwindCSS）透過 HTTP 與後端（FastAPI）交互，後端處理業務邏輯，存取 MySQL（多租戶資料庫）和 Redis（快取） [cite: 11][cite_start]。LINE Bot 透過 webhook 發送通知，IoT 和區塊鏈模組模擬數據儲存至 MySQL，前端以 Chart.js 展示 ESG 和 IoT 數據 [cite: 1, 11][cite_start]。GitHub Actions 負責 CI/CD，自動化測試與部署 [cite: 11]。[cite_start]Q: 為什麼選擇 FastAPI 和 Vue.js？ A: FastAPI 提供高效能非同步 API，支援 Pydantic 驗證，適合高併發農業數據處理 [cite: 11][cite_start]。Vue.js 輕量、響應式，搭配 Pinia 和 TailwindCSS，快速實現數據可視化 [cite: 11][cite_start]。兩者開源生態活躍，降低維護成本，適合 SaaS 快速迭代 [cite: 11]。[cite_start]Q: 如何實現多租戶？對資料隔離和安全性有何影響？ A: 多租戶透過 MySQL 的 tenant_id 欄位實現 [cite: 1][cite_start]。核心表（如 tenants, farmers, products, orders）包含此欄位 [cite: 1][cite_start]。API 透過 JWT 驗證 tenant_id，確保數據隔離，防止跨租戶洩漏，提升安全性 [cite: 1]。[cite_start]Q: 使用了哪些第三方服務或 API？如何整合？ A: 使用 LINE Bot（通知）、Stripe 和 NewebPay（模擬支付） [cite: 1][cite_start]。LINE Bot 透過 line-bot-sdk 整合，FastAPI 處理 webhook 與推播，需配置 LINE_CHANNEL_ACCESS_TOKEN 和 LINE_CHANNEL_SECRET [cite: 1][cite_start]。支付模擬交易流程，數據儲存於 MySQL [cite: 1]。2. 後端 (FastAPI) 相關[cite_start]Q: FastAPI 如何設計 JWT 認證？Token 包含哪些資訊？ A: 使用 PyJWT 實現，用戶登入後生成包含 user_id, tenant_id, role, exp 的 Token [cite: 12][cite_start]。API 路由透過 Depends(get_current_user) 解碼，驗證 tenant_id 確保多租戶隔離 [cite: 12][cite_start]。Token 存於前端 localStorage，請求攜帶於 Authorization: Bearer <token> [cite: 12]。[cite_start]Q: 分離 api/routes/farmers.py 和 api/routes/auth.py 的好處？ A: 分離路由實現模組化，farmers.py 處理農民 CRUD，auth.py 專注認證邏輯，降低耦合，提升可維護性與可測試性，方便獨立擴展 [cite: 12]。[cite_start]Q: ESG 報告計算邏輯如何實現？如何擴展新指標？ A: 在 services/esg_calculator.py 中，根據銷售數據、IoT 環境數據（用水量）與治理數據（交易透明度）加權計算 ESG 分數，使用 Pandas 和 scikit-learn [cite: 13][cite_start]。擴展新指標需更新 schemas/esg.py 模型，新增計算函數，並調整前端 Chart.js 配置 [cite: 13]。[cite_start]Q: 如何處理 IoT 數據的即時性和歷史數據？ A: 模擬 IoT 數據（services/iot.py）定期生成並儲存至 MySQL 的 iot_data 表 [cite: 13][cite_start]。Redis 快取最新數據降低資料庫壓力 [cite: 13][cite_start]。歷史數據透過 SQLAlchemy 按時間查詢，前端 Chart.js 展示趨勢圖 [cite: 13]。[cite_start]Q: 區塊鏈模組的角色？未來整合考慮？ A: 模擬區塊鏈（services/blockchain.py）記錄交易哈希、時間戳、訂單 ID，儲存於 MySQL，展示供應鏈透明概念 [cite: 13][cite_start]。未來整合（如 Ethereum）需考慮智能合約設計、Web3.py 整合、Gas 費用與私鑰安全 [cite: 13]。[cite_start]Q: api/main.py 環境變數驗證如何防止錯誤？ A: 使用 pydantic_settings 的 BaseSettings 驗證 JWT_SECRET_KEY, DATABASE_URL 等變數，啟動時檢查格式，缺失或錯誤會拋異常，防止配置錯誤 [cite: 13]。[cite_start]Q: create_initial_data 函數的作用？ A: 在 api/main.py，create_initial_data 於啟動時檢查並插入預設租戶與角色數據，確保首次部署或測試環境具備最小運行條件 [cite: 13]。[cite_start]Q: 後端訂單管理與 LINE 通知如何實現？ A: 在 api/routes/orders.py，訂單管理支援多租戶隔離與 LINE 通知 [cite: 13][cite_start]。透過 POST /api/v1/orders 創建訂單，驗證 tenant_id 確保隔離，儲存至 MySQL 的 orders 表，使用 line-bot-sdk 推送訊息至 line_user_id，包含訂單詳情（如商品 ID、數量） [cite: 13]。3. 前端 (Vue.js) 相關[cite_start]Q: 前端如何處理登入、登出與 JWT 驗證？ A: LoginView.vue 透過 axios.post('/api/v1/auth/login') 提交帳密，獲取 JWT 存於 localStorage，Pinia（stores/auth.js）管理認證狀態 [cite: 13][cite_start]。登出清除 localStorage 和 Pinia 狀態，重定向至登入頁 [cite: 13][cite_start]。API 請求攜帶 Authorization: Bearer <token> [cite: 13]。[cite_start]Q: DashboardView.vue 如何處理錯誤？為什麼重要？ A: 使用 vue-toastification 顯示錯誤提示 [cite: 13][cite_start]。try-catch 包裝 axios 請求，失敗時觸發 toast（如 this.$toast.error('載入數據失敗')），這提供清晰用戶回饋，提升體驗，並便於除錯 [cite: 13]。[cite_start]Q: DashboardView.vue 如何整合 Chart.js？ A: 在 DashboardView.vue，透過 axios.get('/api/v1/esg-report') 獲取 ESG 數據，於 onMounted 勾子使用 Chart.js 渲染柱狀圖，展示環境、社會、治理分數 [cite: 13][cite_start]。配置 type="module" 確保 ES 模組相容，responsive: true 適應不同設備 [cite: 13]。[cite_start]Q: 前端顯示區塊鏈交易記錄時關注哪些數據點？ A: 顯示交易哈希、時間戳、訂單 ID 和租戶 ID [cite: 13][cite_start]。透過 axios.get('/api/v1/blockchain-transactions') 獲取數據，並在表格中展示，增強供應鏈透明度 [cite: 13]。[cite_start]Q: LINE 通知如何實現動態用戶 ID 輸入和驗證？ A: NotificationView.vue 提供輸入欄，透過 axios.post('/api/v1/notifications/send-line-message') 發送用戶 ID [cite: 13][cite_start]。後端驗證格式並記錄於 users 表，使用 line-bot-sdk 推播訊息 [cite: 13]。[cite_start]Q: Pinia 狀態管理的優點是什麼？ A: Pinia 輕量、支援 Composition API，語法簡潔，與 Vue DevTools 整合良好，便於除錯與狀態追蹤，適合管理認證與數據狀態 [cite: 13]。[cite_start]Q: 前端的 API 請求如何統一管理？ A: 在 frontend/src/api/index.js，使用 axios.create 定義基礎 URL 和標頭（如 Authorization） [cite: 13][cite_start]。各模組（如 auth, orders）獨立函數，降低耦合，方便維護 [cite: 13]。4. DevOps 與部署Q: CI/CD 管線的各階段負責什麼？ A: .github/workflows/ci.yml 包含：[cite_start]Linting：Flake8、Bandit（後端），ESLint（前端）檢查程式碼 [cite: 14, 24, 25]。[cite_start]Testing：Pytest（後端），Vitest（前端）執行測試 [cite: 14]。[cite_start]Build：建構 Docker 映像 [cite: 14]。[cite_start]Push：推送至 Docker Hub [cite: 14]。[cite_start]Deploy：透過 SSH 部署至 VPS 或 Vercel [cite: 14]。[cite_start]Q: 為什麼採用多階段 Dockerfile？ A: 多階段 Dockerfile（api/Dockerfile, frontend/Dockerfile）分建構與運行階段，減少映像大小（約 30-50%），移除不必要工具，提升安全性 [cite: 14]。[cite_start]Q: Docker Compose 配置包含哪些服務？為什麼需要健康檢查？ A: 包含 api (FastAPI), frontend (Vue 3), mysql, redis, phpmyadmin [cite: 14][cite_start]。健康檢查（healthcheck）確保服務啟動正常（如 MySQL 可連線），避免依賴未就緒 [cite: 14]。[cite_start]Q: 如何在 CI/CD 中執行測試？ A: 後端使用 Pytest（pytest tests/api/），前端使用 Vitest（npm run test） [cite: 14][cite_start]。CI 環境設置 MySQL 和 Redis 容器，確保測試隔離 [cite: 14]。[cite_start]Q: Vercel 如何用於前端部署？ A: frontend/vercel.json 定義路由與環境變數 [cite: 6][cite_start]，vercel --prod 部署 Vite 建構輸出（dist/），提供 CDN 和 HTTPS 支援 [cite: 6]。5. 軟體工程實踐[cite_start]Q: 專案如何體現模組化設計？ A: 後端路由分離（routes/）、前端組件化（components/, views/）及服務分離（LINE Bot、IoT），降低耦合，方便維護與擴展 [cite: 15]。[cite_start]Q: 如何確保可測試性？ A: 使用 Pytest 和 Vitest 編寫單元與整合測試，依賴注入與 mock 技術確保隔離，CI 強制執行測試 [cite: 15]。[cite_start]Q: 開發過程中遇到哪些挑戰？如何解決？ A: 挑戰包括多租戶隔離（用 tenant_id 過濾）、LINE webhook 配置（用 ngrok 測試）、IoT 數據模擬（定時任務與 Redis 快取）、API 一致性（Pydantic 與 OpenAPI 文件） [cite: 15]。[cite_start]Q: 若有更多時間，會優先改進什麼？ A: 實現真實區塊鏈整合（如 Ethereum）與 IoT 即時數據流，提升交易透明度與數據價值 [cite: 15]。6. 環境需求[cite_start]Docker 與 Docker Compose（推薦） [cite: 1, 15][cite_start]Python 3.11+（本地後端開發） [cite: 16][cite_start]Node.js 18+（本地前端開發） [cite: 17][cite_start]Git [cite: 15][cite_start]LINE 開發者帳戶（LINE Bot 整合，開發環境可選） [cite: 1][cite_start]MySQL 8.0（資料庫） [cite: 1, 18][cite_start]Redis 7.0（快取） [cite: 1, 18]7. 安裝與設置[cite_start]本專案僅提供核心代碼，外部套件需手動安裝 [cite: 1]。複製儲存庫：git clone https://github.com/BpsEason/agribridge-saas.git
cd agribridge-saas
[cite_start][cite: 16]安裝系統級依賴（若不使用 Docker）：Python 3.11：# Ubuntu/Debian
sudo apt update
sudo apt install python3.11 python3-pip
# macOS (via Homebrew)
brew install python@3.11
[cite_start][cite: 16]Node.js 18：# Ubuntu/Debian
curl -fsSL https://deb.nodesource.com/setup_18.x | sudo -E bash -
sudo apt install -y nodejs
# macOS (via Homebrew)
brew install node@18
[cite_start][cite: 17]MySQL 8.0：# Ubuntu/Debian
sudo apt install mysql-server
sudo systemctl start mysql
# macOS (via Homebrew)
brew install mysql
brew services start mysql
[cite_start][cite: 18]Redis 7.0：# Ubuntu/Debian
sudo apt install redis-server
sudo systemctl start redis
# macOS (via Homebrew)
brew install redis
brew services start redis
[cite_start][cite: 18]設置環境變數：複製 .env 範本：cp .env.example .env
[cite_start][cite: 19]更新 .env：[cite_start]JWT_SECRET_KEY：執行 openssl rand -base64 32 生成 [cite: 19]。[cite_start]MYSQL_ROOT_PASSWORD、MYSQL_USER、MYSQL_PASSWORD：設置 MySQL 帳密 [cite: 19]。[cite_start]DATABASE_URL：格式為 mysql+pymysql://<user>:<password>@<host>:3306/<database> [cite: 19]。[cite_start]REDIS_URL：格式為 redis://<host>:6379/0 [cite: 19]。[cite_start]LINE_CHANNEL_ACCESS_TOKEN、LINE_CHANNEL_SECRET：從 LINE 開發者控制台取得（開發環境可模擬） [cite: 19]。[cite_start]STRIPE_API_KEY、NEWEPAY_API_KEY：開發環境使用模擬值 [cite: 19]。安裝後端依賴：進入 api/：cd api
[cite_start][cite: 20]安裝套件（依 requirements.txt）：pip install --no-cache-dir fastapi[all] uvicorn pandas scikit-learn redis python-dotenv \
SQLAlchemy PyMySQL pydantic_settings numpy matplotlib PyJWT cryptography \
python-multipart beautifulsoup4 requests html5lib psutil uvloop httpx line-bot-sdk
[cite_start][cite: 20]若有依賴衝突，使用虛擬環境：python -m venv venv
source venv/bin/activate  # Linux/macOS
# .\venv\Scripts\activate   # Windows
pip install -r requirements.txt
[cite_start][cite: 20]安裝前端依賴：進入 frontend/：cd frontend
[cite_start][cite: 21]安裝套件（依 package.json）：npm install axios pinia pinia-plugin-persistedstate vue vue-router vue-toastification \
chart.js vue-chartjs @vitejs/plugin-vue @vue/test-utils @vitest/coverage-v8 \
vite autoprefixer postcss tailwindcss vitest @vue/eslint-config-prettier eslint \
eslint-plugin-vue prettier
[cite_start][cite: 21]初始化資料庫：啟動 MySQL 並建立資料庫：mysql -u root -p
CREATE DATABASE agribridge_db;
[cite_start][cite: 22]執行初始數據腳本：cd api
python -c "from main import create_initial_data; create_initial_data()"
[cite_start][cite: 13]8. 運行應用程式使用 Docker Compose（推薦）：docker-compose up --build -d
[cite_start][cite: 23][cite_start]前端：http://localhost:5173 [cite: 23][cite_start]API：http://localhost:8000/api/v1 [cite: 23][cite_start]phpMyAdmin：http://localhost:8080 [cite: 23]本地運行：後端：cd api
uvicorn main:app --host 0.0.0.0 --port 8000 --reload
[cite_start][cite: 23]前端：cd frontend
npm run dev
[cite_start][cite: 23]停止服務：docker-compose down
[cite_start][cite: 23]9. LINE Bot 配置[cite_start]在 LINE 開發者控制台建立官方帳號，取得 LINE_CHANNEL_ACCESS_TOKEN 和 LINE_CHANNEL_SECRET [cite: 24]。[cite_start]更新 .env 文件 [cite: 19, 24]。[cite_start]設定 webhook URL 為 http://<your-domain>/api/v1/line-webhook [cite: 24]。[cite_start]測試通知（前端儀表板或 /api/v1/notifications/send-line-message） [cite: 24]。10. 測試後端測試（Pytest）：cd api
pytest ../tests/api/
[cite_start][cite: 24]前端測試（Vitest）：cd frontend
npm run test
[cite_start][cite: 24]程式碼檢查：後端：cd api
pip install flake8 bandit
flake8 .
bandit -r .
[cite_start][cite: 24, 25]前端：cd frontend
npm run lint
[cite_start][cite: 24]11. 部署Docker 部署：[cite_start]使用 docker-compose.yml 搭配 Nginx 反向代理 [cite: 24]。[cite_start]確保 .env 安全 [cite: 24]。Vercel（前端）：[cite_start]執行 vercel --prod 部署 [cite: 24, 6]。[cite_start]frontend/vercel.json 定義路由與環境變數 [cite: 6]。VPS 部署：[cite_start]配置 VPS 的 Docker Compose，使用 CI/CD 自動部署 [cite: 24]。12. 常見問題（FAQ）[cite_start]Q: 前端報錯 Uncaught SyntaxError: Cannot use import statement outside a module 怎麼解決？ A: 這表示 JavaScript 文件未被識別為 ES 模組 [cite: 26]。請檢查：[cite_start]確認 <script> 標籤：確保 frontend/index.html 包含 type="module" [cite: 26]。<script type="module" src="/src/main.js"></script>
[cite_start][cite: 26][cite_start]檢查 Vite 配置：確認 frontend/vite.config.js 正確 [cite: 27, 28]。[cite_start]檢查 package.json：確保 frontend/package.json 包含 "type": "module" [cite: 28]。[cite_start]Vue 檔案：確認 Vue 檔案（如 DashboardView.vue）的 <script> 包含 type="module" [cite: 26]。[cite_start]清除快取：執行 npm cache clean --force 並重新運行 npm install [cite: 26]。[cite_start]使用 Vite 伺服器：透過 npm run dev 運行前端，Vite 自動處理模組解析 [cite: 26]。13. 貢獻指南[cite_start]Fork 儲存庫 [cite: 29]。[cite_start]建立分支（git checkout -b feature/your-feature） [cite: 29]。[cite_start]提交變更（git commit -m "Add your feature"） [cite: 29]。[cite_start]推送分支（git push origin feature/your-feature） [cite: 29]。[cite_start]提交 Pull Request [cite: 29]。14. 授權[cite_start]本專案採用 MIT 授權，詳見 LICENSE 文件 [cite: 29]。[cite_start]AgriBridge - 以 FastAPI、Vue 3、TailwindCSS、Docker 和 MySQL 打造永續農業平台，實現 多租戶、LINE Bot、IoT、區塊鏈 與 ESG 可視化 的高效生態系統 [cite: 29]。
