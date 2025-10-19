# Cheapest価格取得機能の実装

## 概要
Google FlightsからCheapest（最安値順）の価格を取得できるように、`tfu`パラメータの生成機能を実装しました。

## 主な変更ファイル

### 1. `fast_flights/pb/flights.proto`
新しいProtocol Buffer定義を追加しました。

**追加内容:**
```protobuf
// Message for the tfu parameter (price sorting preference)
enum SortType {
  UNKNOWN_SORT = 0;
  BEST = 1;
  CHEAPEST = 2;
}

message SortPreference {
  int32 field1 = 1;  // Always 2
  SortType sort_type = 4;
  int32 field5 = 5;  // 20 for Best, 21 for Cheapest
}

message TfuData {
  SortPreference preference = 2;
  bytes field4 = 4;  // Empty bytes
}
```

**理由:**
- Google Flightsの`tfu`パラメータの構造を定義
- BestとCheapestの2つのソートタイプをサポート

---

### 2. `fast_flights/querying.py`

#### 2-1. インポートの追加
```python
from .pb.flights_pb2 import (
    Airport, FlightData, Info, Passenger, Seat,
    SortPreference, SortType, TfuData, Trip  # 追加
)
```

#### 2-2. 新しいメソッド `_get_tfu_param()` の追加
```python
def _get_tfu_param(self) -> str:
    """Get the tfu parameter for price sorting."""
    if self.price_type == "best":
        # Best: field1=2, sort_type=1 (BEST), field5=20
        sort_pref = SortPreference(field1=2, sort_type=SortType.BEST, field5=20)
    else:  # cheapest
        # Cheapest: field1=2, sort_type=2 (CHEAPEST), field5=21
        sort_pref = SortPreference(field1=2, sort_type=SortType.CHEAPEST, field5=21)

    tfu_data = TfuData(preference=sort_pref, field4=b"")
    # Serialize and manually append field4 empty bytes (0x22 0x00)
    # Protobuf normally skips empty fields, but Google includes this
    serialized = tfu_data.SerializeToString()
    # Append field 4 (wire type 2) with length 0: 0x22 (field 4, type 2) + 0x00 (length 0)
    serialized += bytes([0x22, 0x00])
    # Remove padding to match Google's format
    return b64encode(serialized).decode("utf-8").rstrip("=")
```

**理由:**
- `price_type`に基づいて正しい`tfu`パラメータを生成
- Protobufは空フィールドをスキップするため、手動で`field4`を追加
- Base64パディングを削除してGoogleのフォーマットに一致

#### 2-3. `url()` メソッドの修正
**変更前:**
```python
if self.price_type == "cheapest":
    url += "&tfu=EgoIABAAGAAgAigD&hl"
```

**変更後:**
```python
# Always include tfu parameter for price sorting
url += "&tfu=" + self._get_tfu_param()
```

**理由:**
- 固定値から動的生成に変更
- BestとCheapest両方に対応

#### 2-4. `params()` メソッドの修正
**変更前:**
```python
params = {"tfs": self.to_str(), "hl": self.language, "curr": self.currency}

if self.price_type == "cheapest":
    params["tfu"] = "EgoIABAAGAAgAigD&hl"

return params
```

**変更後:**
```python
params = {
    "tfs": self.to_str(),
    "hl": self.language,
    "curr": self.currency,
    "tfu": self._get_tfu_param(),  # Always include tfu parameter
}
return params
```

**理由:**
- 常に`tfu`パラメータを含めるように変更
- コードの一貫性向上

---

### 3. `fast_flights/pb/flights_pb2.py` と `flights_pb2.pyi`
Protocol Bufferコンパイラによって自動生成されたファイルです。
- 新しい`SortType` enum
- 新しい`SortPreference`と`TfuData`クラス

---

## tfuパラメータの値

Chrome DevToolsで調査した結果、以下の値が正しいことを確認しました：

| 種類 | Base64値 | 説明 |
|------|----------|------|
| **Best** | `EgYIAiABKBQiAA` | field1=2, sort_type=1, field5=20 |
| **Cheapest** | `EgYIAiACKBUiAA` | field1=2, sort_type=2, field5=21 |

---

## 使用例

### 基本的な使い方
```python
from fast_flights import create_query, get_flights, FlightQuery, Passengers

query = create_query(
    flights=[
        FlightQuery(
            date="2025-12-19",
            from_airport="MYJ",
            to_airport="LON"
        )
    ],
    seat="economy",
    trip="one-way",
    passengers=Passengers(adults=1),
    language="en-US",
    price_type="cheapest"  # ← Cheapest価格を取得
)

flights = get_flights(query)

# 結果の表示
for flight in flights[:5]:
    print(f"{flight.price:,} - {', '.join(flight.airlines)}")
```

### 実行結果（例）
```
✓ Found 16 flights

Top 5 cheapest flights:
  1. 54,848 - Jeju Air, Shenzhen
  2. 65,344 - IBEX, Spring, China Southern
  3. 65,887 - Jetstar, China Southern
  4. 66,445 - Jeju Air, China Eastern
  5. 66,445 - Jeju Air, China Eastern
```

---

## テスト済み環境
- Python 3.10+
- Google Flights（2025年10月時点）
- Route: MYJ (Matsuyama) → LON (London)
- Date: 2025-12-19

---

## 技術的詳細

### プロトコルバッファのワイヤーフォーマット
```
Best: 12 06 08 02 20 01 28 14 22 00
      │  │  │  │  │  │  │  │  └─ field4 (empty, length 0)
      │  │  │  │  │  │  │  └───── field4 key (0x22)
      │  │  │  │  │  │  └───────── field5 value (20)
      │  │  │  │  │  └──────────── field5 key (0x28)
      │  │  │  │  └─────────────── sort_type value (1 = BEST)
      │  │  │  └────────────────── field4 key (0x20)
      │  │  └───────────────────── field1 value (2)
      │  └──────────────────────── field1 key (0x08)
      └─────────────────────────── field2 key + length (6)
```

### 注意点
1. Protobufは通常、空のフィールドをシリアライズ時にスキップしますが、Googleは`field4`（空のbytes）を含めています
2. そのため、手動で`bytes([0x22, 0x00])`を追加する必要があります
3. Base64パディング（`=`）を削除してGoogleのフォーマットに一致させています

---

## 今後の改善点
- ✅ Cheapest価格の取得 - **完了**
- ⚠️ Best価格のパース処理にエラーがある可能性（既存の問題）
- 📝 他のソートオプション（duration, best timeなど）の調査

---

## ユーザーによるコードスタイルの改善

### `fast_flights/querying.py`

#### 1. インポート文の順序を修正
**修正前:**
```python
from base64 import b64encode
from datetime import datetime as Datetime
from dataclasses import dataclass
```

**修正後:**
```python
from base64 import b64encode
from dataclasses import dataclass
from datetime import datetime as Datetime
```
→ 標準ライブラリのインポートをアルファベット順に整理

#### 2. インポートの順序を整理
```python
from .pb.flights_pb2 import Airport, FlightData, Info, Passenger, Seat, SortPreference, SortType, TfuData, Trip
```
→ インポートする名前をアルファベット順に整理

#### 3. Trailing commaの追加
```python
params = {
    "tfs": self.to_str(),
    "hl": self.language,
    "curr": self.currency,
    "tfu": self._get_tfu_param(),  # ← カンマを追加
}
```
→ 最後の要素にもカンマを追加（Pythonのベストプラクティス）

#### 4. Assert文を1行に整理
**修正前:**
```python
assert (
    sum((adults, children, infants_in_seat, infants_on_lap)) <= 9
), "Too many passengers (> 9)"
assert (
    infants_on_lap <= adults
), "Must have at least one adult per infant on lap"
```

**修正後:**
```python
assert sum((adults, children, infants_in_seat, infants_on_lap)) <= 9, "Too many passengers (> 9)"
assert infants_on_lap <= adults, "Must have at least one adult per infant on lap"
```
→ 簡潔な1行記述に変更

### `example_cheapest.py`

#### 1. インポート文を1行に整理
**修正前:**
```python
from fast_flights import create_query, get_flights, FlightQuery, Passengers
```

**修正後:**
```python
from fast_flights import FlightQuery, Passengers, create_query, get_flights
```
→ インポートする名前をアルファベット順に整理

#### 2. 関数呼び出しの引数を1行に整理
**修正前:**
```python
flights=[
    FlightQuery(
        date="2025-12-19",
        from_airport="MYJ",
        to_airport="LON"
    )
],
```

**修正後:**
```python
flights=[FlightQuery(date="2025-12-19", from_airport="MYJ", to_airport="LON")],
```
→ シンプルな引数は1行で記述

#### 3. Trailing commaの追加
```python
price_type="cheapest",  # ← カンマを追加
```

---

---

## 便コード（フライトナンバー）の取得機能を追加

### 変更ファイル

#### 1. `fast_flights/model.py`

`SingleFlight`データクラスに`flight_number`フィールドを追加しました。

```python
@dataclass
class SingleFlight:
    from_airport: Airport
    to_airport: Airport
    departure: SimpleDatetime
    arrival: SimpleDatetime
    duration: Annotated[int, "(minutes)"]
    plane_type: str
    flight_number: str  # Format: "AA123" (airline code + flight number)
```

**フォーマット:** `[航空会社コード][便番号]`
- 例: `7G23`, `JL221`, `NH3821`

#### 2. `fast_flights/parser.py`

パーサーに便コード取得ロジックを追加しました。

```python
# Flight number: single_flight[22] = [airline_code, flight_num, None, airline_name]
flight_info = single_flight[22]
flight_number = f"{flight_info[0]}{flight_info[1]}" if flight_info else ""

sg_flights.append(
    SingleFlight(
        from_airport=from_airport,
        to_airport=to_airport,
        departure=departure,
        arrival=arrival,
        duration=duration,
        plane_type=plane_type,
        flight_number=flight_number,  # ← 追加
    )
)
```

### データ構造

Google Flightsのデータでは、`single_flight[22]`に便コード情報が配列形式で格納されています：

```python
['7G', '23', None, 'Star Flyer']
# ↓
# [0]: 航空会社コード
# [1]: 便番号
# [2]: None（未使用）
# [3]: 航空会社名
```

### 使用例

```python
from fast_flights import create_query, get_flights, FlightQuery, Passengers

query = create_query(
    flights=[FlightQuery(date="2025-12-19", from_airport="HND", to_airport="KIX")],
    seat="economy",
    trip="one-way",
    passengers=Passengers(adults=1),
    language="en-US",
)

flights = get_flights(query)

for flight in flights[:3]:
    print(f"{', '.join(flight.airlines)} - ¥{flight.price:,}")
    for segment in flight.flights:
        print(f"  Flight {segment.flight_number}: {segment.from_airport.code} → {segment.to_airport.code}")
        print(f"    Departure: {segment.departure.time}")
        print(f"    Aircraft: {segment.plane_type}")
```

### 実行結果（例）

```
Star Flyer - ¥10,610
  Flight 7G23: HND → KIX
    Departure: [12]
    Aircraft: Airbus A320

JAL - ¥11,219
  Flight JL221: HND → KIX
    Departure: [7]
    Aircraft: Boeing 737

ANA - ¥11,219
  Flight NH3821: HND → KIX
    Departure: [8, 45]
    Aircraft: Airbus A320
```

### 変更による影響

この変更により、既存のコードで`SingleFlight`を生成する際に`flight_number`パラメータが必須になります。
パーサー以外で`SingleFlight`を直接インスタンス化している場合は、`flight_number`を追加する必要があります。

---

# Multi-city（複数都市周遊便）のサポート状況

## 概要
Multi-cityクエリのサポート状況を調査し、技術的な制限を明確にしました。

## サポート状況

### ✅ 2区間のmulti-city（往復型）
- **例**: HND → KIX → HND
- **状態**: 完全サポート
- **動作**: 初期HTMLレスポンスにフライトデータが含まれる
- **実装**: 既存の`fetch_flights_html()`で取得可能

### ✅ 3区間以上のmulti-city
- **例**: HND → ICN → FUK → HND  
- **状態**: 完全サポート（GetShoppingResults API経由）
- **実装**: 自動的にAPIコールを使用してフライトデータを取得

## 技術的な詳細

### データソースの違い

#### 2区間のmulti-city
- 初期HTMLレスポンスの`script.ds\:1`タグに直接フライトデータが含まれる
- 従来の`fetch_flights_html()`でデータ取得可能

#### 3区間以上のmulti-city ✅ 実装済み
- 初期HTMLにはフライトデータが**含まれない**
- JavaScriptが`GetShoppingResults` APIエンドポイントを**動的に**呼び出してデータを取得
- APIエンドポイント: `https://www.google.com/_/FlightsFrontendUi/data/travel.frontend.flights.FlightsFrontendService/GetShoppingResults`
- このAPIは複雑なリクエストボディと特殊なヘッダー（`x-same-domain`, `x-goog-ext-259736195-jspb`など）を必要とする

### 実装方法
3区間以上のmulti-cityクエリを検出すると、自動的にGetShoppingResults APIを直接呼び出します：

1. **リクエストボディの生成** (`_build_api_request_body`)
   - クエリデータ（フライト情報、座席クラス、乗客数）をJSON配列に変換
   - URL-encoded形式で`f.req`パラメータとして送信

2. **APIコール** (`fetch_flights_via_api`)
   - POSTリクエストでAPIエンドポイントを呼び出し
   - 必要なヘッダー（`x-same-domain`, `x-goog-ext-259736195-jspb`）を設定
   - browser impersonation (`primp`)を使用して実際のブラウザのように動作

3. **レスポンスのパース**
   - XSS保護プレフィックス `)]}'` を除去
   - JSON配列から内部のフライトデータを抽出
   - HTMLライクな構造に変換して既存のパーサーと互換性を保つ

4. **自動切り替え**
   ```python
   if isinstance(q, Query) and q.trip == 3 and len(q.flight_data) >= 3:
       return fetch_flights_via_api(q, proxy=proxy)
   ```

## パーサーの変更
`fast_flights/parser.py`の`parse_js`関数を更新し、`data[3]`が`None`の場合に適切なエラーメッセージを表示するようにしました：

```python
# Check if flight data exists
if data[3] is None:
    raise ValueError(
        "No flight data found in response. "
        "This may occur with: "
        "(1) Multi-city queries with 3+ legs (currently unsupported), "
        "(2) No available flights for the requested route/dates, "
        "(3) Invalid query parameters. "
        "Note: Multi-city queries with 2 legs are supported."
    )
```

## サンプルコード

### 2区間のmulti-city（動作する）
```python
from fast_flights import create_query, FlightQuery, Passengers, get_flights

query = create_query(
    flights=[
        FlightQuery(date="2025-12-25", from_airport="HND", to_airport="KIX"),
        FlightQuery(date="2025-12-28", from_airport="KIX", to_airport="HND"),
    ],
    seat="economy",
    trip="multi-city",
    passengers=Passengers(adults=1),
    language="en-US",
    price_type="cheapest",
)

flights = get_flights(query)  # ✓ 動作する
```

### 3区間のmulti-city（動作する）
```python
query = create_query(
    flights=[
        FlightQuery(date="2025-12-25", from_airport="HND", to_airport="ICN"),
        FlightQuery(date="2026-01-01", from_airport="ICN", to_airport="FUK"),
        FlightQuery(date="2026-02-18", from_airport="FUK", to_airport="HND"),
    ],
    seat="economy",
    trip="multi-city",
    passengers=Passengers(adults=1),
    language="en-US",
    price_type="cheapest",
)

flights = get_flights(query)  # ✓ 動作する（APIコールを自動使用）
# 結果: 8件のフライトオプションが見つかりました
```

## 関連ファイル
- `fast_flights/fetcher.py` - API呼び出し実装
- `fast_flights/parser.py` - パーサーの更新  
- `example_multi_city.py` - 2区間のサンプルコード
- `example_3leg_multi_city.py` - 3区間のサンプルコード（APIデモ）
- `test_multi_city.py` - 2区間のテストコード

## 新機能の詳細

### APIコールの流れ
1. ユーザーが3区間以上のmulti-cityクエリを作成
2. `fetch_flights_html()`が自動的に`fetch_flights_via_api()`を呼び出し
3. APIリクエストボディを構築（クエリデータ→JSON配列→URL-encoded）
4. POSTリクエストでGetShoppingResults APIを呼び出し
5. レスポンスをパースしてHTMLライクな構造に変換
6. 既存のパーサー（`parse_js`）でフライトデータを抽出

### 利点
- **透過的**: ユーザーコードの変更不要
- **自動切り替え**: 2区間はHTML、3区間以上はAPI
- **互換性**: 既存のパーサーとの完全互換
- **高速**: Playwrightを使わずに直接APIコール

---

## 関連ファイル
- `fast_flights/pb/flights.proto` - Protocol Buffer定義
- `fast_flights/querying.py` - クエリ生成ロジック
- `fast_flights/model.py` - データモデル
- `fast_flights/parser.py` - HTMLパーサー
- `example_cheapest.py` - 使用例
- `CHANGES.md` - 変更履歴（このファイル）

