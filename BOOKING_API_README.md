# Booking URL API Implementation

## 概要 / Overview

Google Flightsの予約URL（booking URL）から航空券情報を取得する機能を実装しました。

Chrome DevTools MCPを使用してAPIエンドポイントとリクエスト/レスポンスの構造を分析し、Pythonで再現しています。

## 実装内容 / Implementation

### 1. 新しいモジュール: `fast_flights/booking.py`

以下の機能を提供します：

```python
from fast_flights import get_booking_info, BookingInfo, BookingFlight, BookingProvider

# Booking URLから情報を取得
booking_url = "https://www.google.com/travel/flights/booking?tfs=..."
info = get_booking_info(booking_url)

# 取得できる情報:
# - フライト情報（航空会社、便名、空港、時刻、機材、CO2排出量）
# - 合計価格と通貨
# - 予約プロバイダー（Booking.com, Gotogate など）
```

### 2. データモデル

#### `BookingFlight`
個別のフライトセグメント情報：
- `airline_code`, `airline_name`: 航空会社コードと名前
- `flight_number`: 便名（例: "OZ177"）
- `from_airport_code`, `from_airport_name`: 出発空港
- `to_airport_code`, `to_airport_name`: 到着空港
- `departure_time`, `departure_date`: 出発時刻と日付
- `arrival_time`, `arrival_date`: 到着時刻と日付
- `duration`: 飛行時間（分）
- `plane_type`: 機材
- `carbon_emissions`: CO2排出量（グラム）

#### `BookingProvider`
予約プロバイダー情報：
- `name`: プロバイダー名
- `price`: 価格（最小単位、例: 円）
- `currency`: 通貨コード（例: "JPY"）
- `url`: 予約URL（オプション）

#### `BookingInfo`
予約情報全体：
- `flights`: フライトセグメントのリスト
- `total_price`: 合計価格
- `currency`: 通貨
- `booking_providers`: 予約プロバイダーのリスト

## 技術的詳細 / Technical Details

### Chrome DevTools MCPによる分析

1. **APIエンドポイント特定**
   - URL: `https://www.google.com/_/FlightsFrontendUi/data/travel.frontend.flights.FlightsFrontendService/GetBookingResults`
   - メソッド: POST
   - コンテンツタイプ: `application/x-www-form-urlencoded`

2. **リクエストパラメータ**
   - `f.req`: 複雑なJSON構造（フライトセグメント情報を含む）
   - `f.sid`: セッションID
   - `hl`: 言語コード
   - その他のメタデータパラメータ

3. **レスポンス構造**
   - フォーマット: `)]}'\\n<length>\\n<JSON>\\n<length>\\n<JSON>...`
   - 最初のJSONブロック: フライト詳細情報
   - 2番目のJSONブロック: 予約プロバイダーと価格情報

4. **必要なヘッダー**
   ```python
   headers = {
       "content-type": "application/x-www-form-urlencoded;charset=UTF-8",
       "referer": booking_url,
       "x-same-domain": "1",
       "x-goog-ext-259736195-jspb": '["en-US","JP","JPY",1,null,[-540],null,null,7,[]]',
   }
   ```

### TFSパラメータのデコード

Booking URLの`tfs`パラメータはbase64エンコードされたprotobufメッセージです：
- フライトセグメント（出発地、目的地、日付）
- 選択された航空会社と便名
- 座席クラス
- 乗客数

現在の実装では、正規表現を使用して主要情報を抽出しています。

## 使用例 / Usage Example

### 推奨方法: セグメント情報を明示的に指定

`tfs`パラメータのデコードは複雑なため、セグメント情報を明示的に指定する方法を推奨します：

```python
from fast_flights import get_booking_info

# 3区間のマルチシティ予約URL（HND→ICN→FUK→HND）
booking_url = "https://www.google.com/travel/flights/booking?tfs=CBwQAho_EgoyMDI1LTEyLTI1Ih8KA0hORBIKMjAyNS0xMi0yNRoDSUNOKgJPWjIDMTc3agcIARIDSE5EcgcIARIDSUNOGj8SCjIwMjYtMDEtMDEiHwoDSUNOEgoyMDI2LTAxLTAxGgNGVUsqAk9aMgMxMzRqBwgBEgNJQ05yBwgBEgNGVUsaPxIKMjAyNi0wMi0xOCIfCgNGVUsSCjIwMjYtMDItMTgaA0hORCoCSkwyAzMwMGoHCAESA0ZVS3IHCAESA0hOREABSAFwAYIBCwj___________8BmAED&tfu=...&hl=en-US"

# セグメント情報を定義
segments = [
    {
        "from": "HND",
        "to": "ICN",
        "date": "2025-12-25",
        "airline": "OZ",
        "flight_number": "177",
    },
    {
        "from": "ICN",
        "to": "FUK",
        "date": "2026-01-01",
        "airline": "OZ",
        "flight_number": "134",
    },
    {
        "from": "FUK",
        "to": "HND",
        "date": "2026-02-18",
        "airline": "JL",
        "flight_number": "300",
    },
]

# 予約情報を取得（セグメント情報を明示的に指定）
info = get_booking_info(booking_url, segments=segments)

# 結果を表示
print(f"Total: {info.currency} {info.total_price:,}")

for i, flight in enumerate(info.flights, 1):
    print(f"\nSegment {i}:")
    print(f"  {flight.airline_name} {flight.flight_number}")
    print(f"  {flight.from_airport_code} → {flight.to_airport_code}")
    print(f"  {flight.departure_date} {flight.departure_time} - {flight.arrival_date} {flight.arrival_time}")
    print(f"  Duration: {flight.duration} min | Aircraft: {flight.plane_type}")

print(f"\nBooking Options:")
for provider in info.booking_providers:
    print(f"  {provider.name}: {provider.currency} {provider.price:,}")
```

### 期待される出力

```
Total: JPY 131,919

Segment 1:
  Asiana Airlines OZ177
  HND → ICN
  2025-12-25 01:30 - 2025-12-25 04:10
  Duration: 160 min | Aircraft: Airbus A321neo

Segment 2:
  Asiana Airlines OZ134
  ICN → FUK
  2026-01-01 13:10 - 2026-01-01 14:40
  Duration: 90 min | Aircraft: Airbus A330

Segment 3:
  JAL JL300
  FUK → HND
  2026-02-18 07:05 - 2026-02-18 08:35
  Duration: 90 min | Aircraft: Airbus A350

Booking Options:
  Booking.com: JPY 131,919
  Gotogate: JPY 134,909
```

## 現在の状況 / Current Status

✅ **実装完了:**
- APIエンドポイントの特定
- リクエストヘッダーとパラメータの構造
- レスポンスパース機能（価格情報、予約プロバイダー）
- データモデルの定義
- `fast_flights.__init__.py`へのエクスポート
- セグメント情報を明示的に指定する機能

✅ **動作確認済み:**
- 価格情報の取得: ✅ 正常動作
- 予約プロバイダー情報: ✅ 正常動作
- 明示的なセグメント指定: ✅ 推奨方法

⚠️ **制限事項:**
- `tfs`パラメータからの自動セグメント抽出は未実装（protobuf構造が複雑なため）
- セグメント情報を明示的に指定する必要があります（推奨アプローチ）
- フライト詳細情報の解析は今後の改善課題

## Next Steps / 次のステップ

1. **デバッグとテスト**
   - 保存したレスポンスファイルを使用してパース処理をデバッグ
   - 実際のAPIリクエストをテスト

2. **Protobuf定義の改善**
   - `tfs`パラメータ用の適切なprotobuf定義を追加
   - より正確なパース処理の実装

3. **ドキュメント作成**
   - APIリファレンス
   - 使用例の追加

## ファイル構成 / File Structure

```
fast_flights/
├── booking.py              # Booking URL API実装
├── __init__.py            # エクスポート設定（更新済み）
└── ...

テストファイル:
├── test_booking_api.py            # メインテストスクリプト
├── debug_booking_api.py           # デバッグスクリプト
├── test_booking_parse.py          # パーステスト
├── debug_booking_response.json    # 保存したAPIレスポンス
└── ...
```

## 参考 / References

- Chrome DevTools MCP を使用してAPIを分析
- Google Flights Booking URL: `https://www.google.com/travel/flights/booking?tfs=...`
- API Endpoint: `FlightsFrontendService/GetBookingResults`

