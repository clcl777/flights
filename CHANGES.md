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

## 関連ファイル
- `fast_flights/pb/flights.proto` - Protocol Buffer定義
- `fast_flights/querying.py` - クエリ生成ロジック
- `example_cheapest.py` - 使用例
- `CHANGES.md` - 変更履歴（このファイル）

