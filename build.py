#!/usr/bin/env python3
"""川助商店 サイト生成スクリプト（日本語 / English）。

使い方:  python3 build.py   → public/（日本語）と public/en/（英語）を生成する。
アプリの追加・修正は下の APPS を編集して再実行するだけ。
各項目は {"ja": ..., "en": ...} の形で両言語を書く。
"""
from pathlib import Path
from html import escape
import json
import re

ROOT = Path(__file__).resolve().parent
OUT = ROOT / "public"

CONTACT_FORM = "https://docs.google.com/forms/d/17X6uGOAXiaTEBY0BAIMWRr_zwo9wxIBRL23ZtDA2-50/viewform"
# Cloudflare Web Analytics（Cookieを使わないアクセス解析）。トークンはHTMLに公開される前提の値。
CF_ANALYTICS_TOKEN = "324dc61d4e5946dbaf548083d5e14584"
APPLE_EULA = "https://www.apple.com/legal/internet-services/itunes/dev/stdeula/"
DEVELOPER_PAGE = {"ja": "https://apps.apple.com/jp/developer/masashi-kawakami/id729354347",
                  "en": "https://apps.apple.com/developer/masashi-kawakami/id729354347"}
SITE = "https://kawasukestore.github.io"
UPDATED = {"ja": "2026年10月12日", "en": "October 12, 2026"}

APPS = [
    {
        "slug": "findsimilarpics",
        "top_plan": 2,  # 購入がいちばん多いプランの pricing の位置
        "popular_note": {"ja": "直近3か月のダウンロード数で川助商店の2番目。有料版も、いちばんよく選ばれているアプリのひとつです。",
                         "en": "Our second most downloaded app over the past three months, and one of our most purchased upgrades."},
        "rank": 2,  # 直近3か月のダウンロード数の順位。サイトには順位だけ出す
        "id": "6760923877",
        "name": {"ja": "類似写真検索", "en": "Similar Photo Search"},
        "full": {"ja": "類似写真検索 - 基準画像からベストショットを厳選", "en": "Similar Photo Search - Pick Your Best Shots"},
        "tagline": {"ja": "似ている写真を並べて比べ、ベストショットだけを残す。",
                    "en": "Compare similar photos side by side and keep only the best shots."},
        "category": {"ja": "写真/ビデオ", "en": "Photo & Video"},
        "os": {"ja": "iOS 18.0 以降", "en": "iOS 18.0 or later"},
        "features": {
            "ja": [
                "基準にする写真を1枚選ぶと、連写や似た構図の写真を類似度（0〜100）付きで一覧表示",
                "検索対象は、iPhoneの「写真」アプリで見られるすべての画像（スクリーンショット・連写の全コマ・iCloud写真も含む。動画と非表示の写真は除く）",
                "2枚を並べた比較ビューで、ズームやスワイプで表情やピントを確認",
                "カレンダーや地図で、日付・撮影場所を絞り込んで検索",
                "お気に入りにした写真は一括削除の対象から外れるので安心",
                "作成したアルバムは色と番号のバッジで、検索結果や比較ビューに表示",
                "画像の解析は端末内で行い、写真をサーバーへ送信しません",
            ],
            "en": [
                "Pick one reference photo to list burst shots and similar compositions with a similarity score (0–100)",
                "Searches every image you can see in the iPhone Photos app, including screenshots, every frame of burst shots and iCloud Photos (videos and hidden photos excluded)",
                "Side-by-side comparison view with zoom and swipe to check expressions and focus",
                "Narrow searches by date or shooting location using the calendar and map",
                "Favorited photos are excluded from bulk deletion",
                "Albums you create appear as colored, numbered badges in results and the comparison view",
                "Images are analyzed on your device and are never uploaded to a server",
            ],
        },
        "updates": {
            "version": "1.9",
            "main": {
                "badge": {"ja": "新機能", "en": "New"},
                "pro": {"ja": "Pro（有料版）の機能です。", "en": "This is a Pro (paid) feature."},
                "title": {"ja": "「写真」アプリから、そのまま類似検索", "en": "Search similar photos straight from the Photos app"},
                "body": {
                    "ja": "iPhoneの「写真」アプリで見ている写真を、共有ボタンから類似写真検索へ送れるようになりました。アプリを開いてから基準画像を探し直す手間がなくなります。",
                    "en": "You can now send the photo you are viewing in the Photos app to Similar Photo Search from the share button — no need to open the app and look for the reference photo again.",
                },
                "steps": [
                    {"img": "screens/findsimilarpics-share-1.jpg",
                     "ja": "「写真」アプリで写真を開き、共有ボタンから「類似写真検索」を選ぶ",
                     "en": "Open a photo in the Photos app, tap Share and choose Similar Photo Search"},
                    {"img": "screens/findsimilarpics-share-2.jpg",
                     "ja": "選んだ写真を確認して「OK」",
                     "en": "Check the photo and tap OK"},
                    {"img": "screens/findsimilarpics-share-3.jpg",
                     "ja": "アプリを開くと、その写真を基準にした検索結果から始まる",
                     "en": "Open the app and it starts with results for that photo"},
                ],
                "note": {
                    "ja": "共有したあとは、ホーム画面から「類似写真検索」を開いてください（1時間以内に開くと、その写真で検索します）。",
                    "en": "After sharing, open Similar Photo Search from your Home Screen (within an hour, it searches with that photo).",
                },
            },
            "extra": [
                {
                    "img": "screens/findsimilarpics-overlay.jpg",
                    "badge": {"ja": "新機能", "en": "New"},
                    "pro": {"ja": "Pro（有料版）の機能です。", "en": "This is a Pro (paid) feature."},
                    "title": {"ja": "「基準画像と重ねて表示する」：2枚をぴったり重ねて違いを見る",
                              "en": "“Overlay with the base image”: line up two photos exactly to spot the difference"},
                    "body": {
                        "ja": "比較画面で、基準画像と類似画像を同じ位置・同じ大きさでぴったり重ねて表示できるようになりました（ワイプ比較）。境界線より左に基準画像、右に類似画像が見え、つまみ（< >）を左右に動かすと、同じ場所が2枚でどう違うかをその場で見比べられます。ほとんど同じに見える連写の中から、ピントや表情、写り込みのわずかな差を見つけるのに便利です。",
                        "en": "The comparison screen can now overlay the reference photo and the similar photo at exactly the same position and size (wipe comparison). The reference photo shows to the left of the dividing line and the similar photo to the right; drag the handle (< >) to see how the very same spot differs between the two. Great for finding tiny differences in focus, expression or stray objects among near-identical burst shots.",
                    },
                    "points": {
                        "ja": [
                            "設定の「比較表示」で「基準画像と重ねて表示する」をオンにすると使えます",
                            "つまみを左右に動かすだけで、境界線のところで基準画像と類似画像が切り替わる",
                            "拡大・移動しても、2枚は同じ位置・同じ倍率で重なったまま",
                        ],
                        "en": [
                            "Turn on “Overlay with the base image” under “Comparison View” in Settings",
                            "Just drag the handle and the two photos switch at the dividing line",
                            "Zoom and pan as you like — the two photos stay aligned at the same position and scale",
                        ],
                    },
                },
            ],
            "others": {
                "ja": [
                    "アプリのアイコンを新しくしました",
                    "検索結果画面の下部（類似度スライダーと「アルバム」「お気に入り」「削除」ボタン）をコンパクトにまとめ、写真の一覧を表示できる範囲を広げました",
                ],
                "en": [
                    "A new app icon",
                    "The controls at the bottom of the results screen (similarity slider and Album, Favorites and Delete buttons) are now more compact, leaving more room for the photo list",
                ],
            },
        },
        "guide": [
            {
                "img": "screens/findsimilarpics-home.jpg",
                "title": {"ja": "ホームから、探したい写真の入り口を選ぶ", "en": "Start from Home to browse your photo library"},
                "body": {
                    "ja": "アプリを開くと、ライブラリ全体の写真枚数やお気に入り・作成したアルバムがカード形式で一覧できます。日付ごとの「カレンダー」や撮影地ごとの「地図」からも写真を選べます。",
                    "en": "The Home screen gives you quick cards for all your photos, favorites, and custom albums. You can also browse by shooting date using the Calendar or by location using the Map.",
                },
                "points": {
                    "ja": [
                        "「すべての写真」や各種スマートアルバム（お気に入り・スクリーンショット等）を網羅",
                        "作成したアルバムには色と番号のバッジが付き、整理状況がひと目でわかる",
                        "右上メニューからアルバム管理・ヘルプ・各種設定にすばやくアクセス",
                    ],
                    "en": [
                        "Quick access to All Photos and smart albums (Favorites, Screenshots, etc.)",
                        "Custom albums show numbered, colored badges so your organization status is clear at a glance",
                        "Top-right buttons provide instant access to Album Management, Help, and Settings",
                    ],
                },
            },
            {
                "img": "screens/findsimilarpics-grid.jpg",
                "title": {"ja": "グリッド一覧で写真を見渡し、基準にする1枚を選ぶ", "en": "Browse the photo grid and choose a reference image"},
                "body": {
                    "ja": "写真をタップするだけで、その写真を基準にした類似写真検索がすぐに始まります。画面下のスライダーで1列〜4列表示を切り替えられ、サムネイルの長押しで拡大プレビューも可能です。",
                    "en": "Simply tap any photo to start a similarity search with it as the reference. Use the slider at the bottom to switch between 1 to 4 columns, and long-press any thumbnail for a full-screen zoom preview.",
                },
                "points": {
                    "ja": [
                        "各写真の右上にあるハートボタンをタップして、その場でお気に入りを切り替え",
                        "1〜2列表示では撮影日とファイル形式（JPG/HEICなど）をカード下に表示",
                        "画面下のスライダーで、一覧性を重視した多列表示と細部確認の拡大表示をスムーズに切り替え",
                    ],
                    "en": [
                        "Tap the heart icon on any photo to toggle favorite status on the spot",
                        "1- and 2-column modes display the shooting date and file format (JPG, HEIC, etc.) below each photo",
                        "Smoothly adjust the bottom slider between high-density multi-column browsing and close-up inspection",
                    ],
                },
            },
            {
                "img": "screens/findsimilarpics-results.jpg",
                "title": {"ja": "類似度スコアと詳細情報を一覧し、まとめて整理", "en": "Review similarity scores, details, and organize in bulk"},
                "body": {
                    "ja": "基準画像と似ている写真が、0〜100のスコア順に一覧表示されます。写真ごとのファイルサイズ、撮影地、撮影日時の比較バーが並び、整理したい写真をチェックして一括操作できます。",
                    "en": "Photos similar to your reference image appear ranked by a 0–100 similarity score. Visual bars for file size, shooting location, and date let you select unwanted duplicates for quick bulk action.",
                },
                "points": {
                    "ja": [
                        "基準画像と同じ日付や50m以内の近接撮影にはチェックマーク（☑）が付いて見分けやすい",
                        "下部のスライダーで「類似度◯◯以上」の表示しきい値を直感的に絞り込み",
                        "選択した写真をワンタップで「アルバムに追加」「お気に入りに追加」「削除」（お気に入り写真は自動で保護）",
                    ],
                    "en": [
                        "Checkmarks (☑) identify shots taken on the same date or within 50 meters of the reference photo",
                        "Use the bottom slider to interactively filter candidates by similarity score threshold",
                        "One-tap bulk actions to Add to Album, Favorite, or Delete (favorited photos are protected from deletion)",
                    ],
                },
            },
            {
                "img": "screens/findsimilarpics-compare.jpg",
                "title": {"ja": "左右並列の比較ビューで、細部のピントや表情を見極める", "en": "Side-by-side comparison to inspect focus and expressions"},
                "body": {
                    "ja": "気になる写真をタップすると全画面の比較ビューが開き、左に基準画像、右に類似画像が並びます。2枚同時にピンチズームやドラッグ移動できるため、連写した顔の表情やピントの微妙な差を精密に見比べられます。",
                    "en": "Tap any photo to open the full-screen comparison view with the reference photo on the left and the candidate on the right. Both images zoom and pan in perfect sync, making subtle differences in focus and facial expressions easy to catch.",
                },
                "points": {
                    "ja": [
                        "画面中央のハンドル（< >）を左右にドラッグして、見たい写真の表示幅を自由に変更（ダブルタップで中央にリセット）",
                        "左右どちらも連動して拡大・縮小・移動し、ダブルタップで拡大切り替え",
                        "「基準画像にする」ボタンで右の写真を新しい基準として即座に再検索",
                    ],
                    "en": [
                        "Drag the center handle (< >) left or right to adjust split width freely (double-tap to reset to center)",
                        "Synchronized pinch-to-zoom and drag panning on both images, with double-tap zoom toggle",
                        "Tap “Make Reference Photo” to instantly restart the search with the candidate photo as the new base",
                    ],
                },
            },
            {
                "img": "screens/findsimilarpics-viewer.jpg",
                "title": {"ja": "大きな画面で1枚ずつ確かめて、「選択」しておく", "en": "Check each photo up close and mark it with “Select”"},
                "body": {
                    "ja": "似ていると判定された写真の中には、基準と関係のない写真が混じることもあります（料理の写真を基準にしたのに、鳥居の写真が並ぶなど）。そんなときは、写真をタップして大きな画面で1枚ずつ中身を確かめ、あとで削除や整理をしたい写真に「選択」を押しておきます。",
                    "en": "Sometimes unrelated photos show up among the matches — a torii gate among food photos, for example. Tap a photo to check it on the big screen one by one, and press “Select” on any photo you want to delete or organize later.",
                },
                "points": {
                    "ja": [
                        "左右の矢印で、次の写真・前の写真へ順に送れる",
                        "右上の目のボタンで基準画像を隠すと、1枚を画面いっぱいに表示（Pro）",
                        "その場で1枚だけ削除・お気に入り・アルバムに追加することもできる",
                    ],
                    "en": [
                        "Use the arrows to move to the next or previous photo",
                        "Hide the reference photo with the eye button to view a match full screen (Pro)",
                        "You can also delete, favorite or add a single photo to an album right there",
                    ],
                },
            },
            {
                "img": "screens/findsimilarpics-selected.jpg",
                "title": {"ja": "一覧に戻っても選択はそのまま。最後にまとめて処理", "en": "Your picks stay selected — handle them all at the end"},
                "body": {
                    "ja": "「閉じる」で一覧に戻っても、大きな画面で「選択」した写真にはチェックが付いたまま残ります。気になる写真をひと通り確かめ終えたら、画面下のボタンで選んだ写真をまとめて処理できます。",
                    "en": "When you close the big screen and return to the list, the photos you selected stay checked. After reviewing everything, handle them all at once with the buttons at the bottom.",
                },
                "points": {
                    "ja": [
                        "削除：いらない写真をまとめて削除",
                        "アルバム：残したい写真をまとめてアルバムに追加",
                        "お気に入り：お気に入りにした写真は、一括削除の対象から外れる",
                    ],
                    "en": [
                        "Delete: remove unwanted photos in one go",
                        "Album: add the keepers to an album together",
                        "Favorites: favorited photos are excluded from bulk deletion",
                    ],
                },
            },
            {
                "img": "screens/findsimilarpics-filter.jpg",
                "title": {"ja": "撮影日・距離・時間・形式で柔軟に絞り込み", "en": "Filter with precision by date, distance, time, and type"},
                "body": {
                    "ja": "検索結果画面の「絞り込み」ボタンから、より条件を絞った抽出が可能です。旅行先での特定の時間帯の写真や、同じ場所・同じファイル形式の写真だけに絞り込んで比較できます。",
                    "en": "Open the Filter sheet from search results to pinpoint photos with precision. Narrow down candidates by a specific time window, shooting distance, or file type to clean up targeted scenes effortlessly.",
                },
                "points": {
                    "ja": [
                        "撮影日：「すべて」「同じ日付のみ」「異なる日付のみ」から選択",
                        "距離フィルター：基準写真の撮影地から半径◯km以内の写真に限定（スライダーで調整可能）",
                        "時間フィルター：基準写真の撮影時刻から前後◯分以内の連写・連続撮影に限定",
                        "「同じタイプ（HEIC/JPG）」や「お気に入り以外」の抽出にも対応",
                    ],
                    "en": [
                        "Date filter: choose from All, Same Date Only, or Different Dates Only",
                        "Distance slider: restrict candidates to within a specific radius (km / miles) of the reference photo",
                        "Time slider: limit results to within a set number of minutes before or after the reference photo",
                        "Toggle switches for Same Type (HEIC/JPG) and Exclude Favorites",
                    ],
                },
            },
            {
                "img": "screens/findsimilarpics-calendar.jpg",
                "title": {"ja": "カレンダーから、撮影した日を選んで探す", "en": "Find photos by shooting date on the calendar"},
                "body": {
                    "ja": "日付ごとの写真撮影枚数がカレンダーの日付下にオレンジ色の数字で表示されます。写真が多く撮られたイベントや旅行の日付をひと目で把握し、タップしてその日の写真一覧を開けます。",
                    "en": "Daily photo counts appear in orange numbers right beneath each date on the calendar. Easily spot high-volume shooting days such as trips and family events, and tap to view photos taken on that day.",
                },
                "points": {
                    "ja": [
                        "月ごとに写真を撮影した日と撮影枚数をわかりやすく可視化",
                        "日付をタップするとその日に撮影された写真グリッドが直接開き、そのまま類似写真検索へ進める",
                        "検索結果の基準画像や候補行の日付をタップして、その日の写真一覧へジャンプすることも可能",
                    ],
                    "en": [
                        "Visual calendar view clearly shows shooting days and photo volume for each month",
                        "Tap any date to open that day's photo grid and jump straight into similarity searching",
                        "Tapping dates in search results also lets you navigate directly to that day's photos",
                    ],
                },
            },
        ],
        "pricing": {"ja": ["基本無料（広告あり・1日の検索回数に上限あり）", "Pro 1か月 ¥100 / 1年 ¥300", "買い切り ¥700"],
                    "en": ["Free with ads (daily search limit)", "Pro: ¥100 / month, ¥300 / year", "Lifetime: ¥700"]},
    },
    {
        "slug": "picdiff",
        "popular_note": {"ja": "直近3か月のダウンロード数で、川助商店の3番目に多いアプリです。",
                         "en": "Our third most downloaded app over the past three months."},
        "rank": 3,  # 直近3か月のダウンロード数の順位。サイトには順位だけ出す
        "top_plan": 2,  # 購入がいちばん多いプランの pricing の位置
        "id": "6790423733",
        "name": {"ja": "画像比較", "en": "Image Compare"},
        "full": {"ja": "画像比較 - 2枚の画像を徹底比較", "en": "Image Compare - Compare Two Images in Detail"},
        "tagline": {"ja": "2枚の画像のズレと違いを、見える形に。",
                    "en": "See exactly how two images are misaligned and how they differ."},
        "category": {"ja": "グラフィック/デザイン", "en": "Graphics & Design"},
        "os": {"ja": "iOS 18.0 以降", "en": "iOS 18.0 or later"},
        "features": {
            "ja": [
                "ブレンド・A/B切替・位置合わせ・差分・スライダーの5つの比較モード",
                "特徴点マッチングで回転・拡大縮小・傾きを補正し、手ぶれした写真も自動で位置合わせ",
                "ピクセル単位の完全一致チェックと、Visionによるシーン類似度の判定",
                "差の大きい部分をヒートマップで強調（感度調整あり）",
                "スライダーモードでは縦横の輝度プロファイルをグラフで表示",
            ],
            "en": [
                "Five comparison modes: blend, A/B toggle, alignment, difference and wipe",
                "Feature-point matching corrects rotation, scale and perspective to align even shaky shots",
                "Pixel-exact match check and Vision-based scene similarity score",
                "Difference heatmap highlights the areas that changed most (adjustable sensitivity)",
                "Wipe mode shows horizontal and vertical luminance profile graphs",
            ],
        },
        "pricing": {"ja": ["基本無料（広告あり）", "月額 ¥100 / 年額 ¥600", "買い切り（全機能）¥1,500", "機能別の買い切り ¥400〜¥800"],
                    "en": ["Free with ads", "¥100 / month, ¥600 / year", "Lifetime, all features: ¥1,500", "Single-feature unlocks: ¥400–¥800"]},
    },
    {
        "slug": "heifconvert",
        "id": "6449701174",
        "name": {"ja": "JPEG/HEIF変換", "en": "JPEG/HEIF Converter"},
        "full": {"ja": "JPEG/HEIF変換 - 画質確認 左右比較 変換前後比較", "en": "JPEG/HEIF Converter - Check Quality Before You Convert"},
        "tagline": {"ja": "iPhoneのHEIC写真を、AIやWebで使いやすいJPEGへすばやく変換。",
                    "en": "Quickly turn iPhone HEIC photos into JPEG, the format AI tools and websites accept most widely."},
        "category": {"ja": "写真/ビデオ", "en": "Photo & Video"},
        "os": {"ja": "iOS 18.0 以降", "en": "iOS 18.0 or later"},
        "features": {
            "ja": [
                "AIチャットやWebサービスに画像を渡すなら、いちばん広く対応しているJPEGが安心。iPhoneで撮ったHEIC写真を、選んですぐJPEGに変換",
                "JPEG ⇄ HEIF の相互変換で、容量の節約や共有時の互換性に対応",
                "変換前後を左右に並べたり切り替えたりして画質を確認",
                "複数の画質で試し、容量と画質の関係をグラフで比較",
                "ファイルサイズ順の並べ替え、形式での絞り込み、スワイプで削除",
                "変換後に元の写真を自動で削除する設定",
            ],
            "en": [
                "JPEG is the safest format to hand an image to AI chats and web services — pick your iPhone HEIC photos and convert them to JPEG right away",
                "Convert JPEG ⇄ HEIF to save storage or improve compatibility when sharing",
                "Check quality with side-by-side or toggle before/after previews",
                "Try several quality levels and compare size vs. quality on a graph",
                "Sort by file size, filter by format, and swipe to delete",
                "Option to delete originals automatically after conversion",
            ],
        },
        "explainer": {
            "title": {"ja": "JPEGとHEIF（HEIC）のちがい", "en": "JPEG vs. HEIF (HEIC)"},
            "lead": {
                "ja": "iPhoneの写真は、多くの場合HEIF（拡張子は.heic）で保存されています。HEIFは容量が小さいのが長所、JPEGはどこでも開けるのが長所です。",
                "en": "iPhone photos are usually saved as HEIF (with the .heic extension). HEIF's strength is its small file size; JPEG's strength is that it opens almost anywhere.",
            },
            "bars": [
                {"label": "JPEG", "pct": 100, "note": {"ja": "大きめ", "en": "Larger"}},
                {"label": "HEIF (HEIC)", "pct": 50, "note": {"ja": "約半分", "en": "About half"}},
            ],
            "bar_caption": {
                "ja": "同じ写真を同じくらいの画質で保存したときの、ファイルサイズのめやす（写真によって変わります）",
                "en": "Typical file size for the same photo at similar quality (varies by photo)",
            },
            "head": {"ja": ["", "JPEG", "HEIF（HEIC）"], "en": ["", "JPEG", "HEIF (HEIC)"]},
            "rows": {
                "ja": [
                    ["拡張子", ".jpg / .jpeg", ".heic / .heif"],
                    ["ファイルサイズ", "大きめ", "約半分（同じくらいの画質で）"],
                    ["互換性（開ける環境）", "◎ ほぼすべての機器・アプリ・Webサービス", "△ iPhone・Mac（iOS 11 / macOS High Sierra 以降）は問題なし。古い機器や一部のアプリ・Webサービスでは開けないことがある"],
                    ["iPhoneでの設定名", "互換性優先", "高効率（標準）"],
                    ["向いている使い方", "人に送る・AIやWebにアップロード・印刷", "iPhoneでの保存・容量の節約"],
                ],
                "en": [
                    ["Extension", ".jpg / .jpeg", ".heic / .heif"],
                    ["File size", "Larger", "About half (at similar quality)"],
                    ["Compatibility", "◎ Almost every device, app and web service", "△ Fine on iPhone and Mac (iOS 11 / macOS High Sierra or later); may not open on older devices or some apps and web services"],
                    ["iPhone setting name", "Most Compatible", "High Efficiency (default)"],
                    ["Best for", "Sending to others, uploading to AI or the web, printing", "Storing on iPhone, saving space"],
                ],
            },
            "tip": {
                "ja": "このアプリなら、送る前や AI・Web に渡す前に HEIC を JPEG へ、保存用に JPEG を HEIF へ。変換前に画質と容量を見比べてから決められます。iPhoneのカメラの保存形式は［設定］＞［カメラ］＞［フォーマット］で選べます。",
                "en": "With this app, convert HEIC to JPEG before sending or handing photos to AI and web services, and JPEG to HEIF for storage — after comparing quality and size first. You can choose the iPhone camera's format in Settings > Camera > Formats.",
            },
            "sources": [
                {"title": {"ja": "Apple サポート「Apple製のデバイスでHEIF／HEVCメディアを扱う」", "en": "Apple Support: Using HEIF or HEVC media on Apple devices"},
                 "url": {"ja": "https://support.apple.com/ja-jp/116944", "en": "https://support.apple.com/en-us/116944"},
                 "note": {"ja": "HEIFはJPEGより圧縮効率が高く、同じくらいの画質のまま容量を節約できる。共有や転送の際、相手が対応していない場合はJPEGに変換されることがある。",
                          "en": "HEIF compresses more efficiently than JPEG, saving space at similar quality; when sharing or transferring, photos may be converted to JPEG if the other device doesn't support HEIF."}},
                {"title": {"ja": "PHILE WEB「iPhoneの写真は『HEIF』『JPEG』どちらを選ぶべき？」（2020年）", "en": "PHILE WEB: HEIF or JPEG for iPhone photos? (2020, Japanese)"},
                 "url": {"ja": "https://www.phileweb.com/sp/review/column/202006/11/1061.html", "en": "https://www.phileweb.com/sp/review/column/202006/11/1061.html"},
                 "note": {"ja": "同じ画素数なら、HEIFのデータ量はJPEGの約半分になる。",
                          "en": "For the same pixel count, a HEIF file is about half the size of a JPEG."}},
            ],
        },
        "pricing": {"ja": ["基本無料（変換機能はすべて無料・画像一覧に広告あり）", "広告の非表示（買い切り）¥500"],
                    "en": ["Free (every conversion feature is free; ads in the image list)", "Remove ads (one-time purchase): ¥500"]},
    },
    {
        "slug": "gengoseireki",
        "top_plan": 2,  # 購入がいちばん多いプランの pricing の位置
        "id": "6780891686",
        "name": {"ja": "元号西暦", "en": "Gengo Seireki"},
        "full": {"ja": "元号西暦 - 年号・干支アプリ", "en": "Gengo Seireki - Japanese Era & Zodiac Converter"},
        "tagline": {"ja": "西暦・元号・干支・天皇・総理大臣を、ひとつの年表で。",
                    "en": "Western years, Japanese eras, zodiac, emperors and prime ministers in one timeline."},
        "category": {"ja": "ユーティリティ", "en": "Utilities"},
        "os": {"ja": "iOS 18.0 以降（iPhone）", "en": "iOS 18.0 or later (iPhone)"},
        "features": {
            "ja": [
                "西暦・元号・干支・天皇・総理大臣を1行に並べた年表（列は最大5つまで入れ替え可能）。南北朝の元号にも対応",
                "年をタップすると今年から何年前か、2つの年をタップすると間の年数と改元回数を表示",
                "干支の表示をオン／オフで切り替え、干支（十干十二支）・十二支・画像付きの十二支から表示形式を選択",
                "人物を登録すると、高校・大学の入学・卒業（生まれ月で早生まれ、浪人にも対応）、七五三・厄年・還暦などの節目の年と、各年の年齢（満年齢・数え年）を年表に表示",
                "源平合戦から第二次世界大戦までの主な合戦・出来事を家紋や国旗つきで表示",
                "お気に入り・履歴の保存、年ごとのメモ（有料版）",
                "時代・元号・干支での絞り込み、文字サイズやふりがな、ダークモードの設定",
            ],
            "en": [
                "A timeline showing Western year, era name, zodiac, emperor and prime minister in one row (up to 5 custom columns), including Northern and Southern Court eras",
                "Tap a year to see how long ago it was; tap two years to see the span and number of era changes",
                "Turn the zodiac on or off with one switch and choose its format: the full sexagenary cycle, the twelve animals, or the twelve animals with images",
                "Register people to show high school and university entry and graduation years (birth month aware, including early-born and gap years), Shichi-Go-San, yakudoshi, kanreki and other milestones, plus each year's age (Western or traditional counting) on the timeline",
                "Major battles and events from the Genpei War to WWII, with family crests and flags",
                "Favorites, history, and per-year notes (paid version)",
                "Filter by period, era or zodiac; adjust text size, furigana and dark mode",
            ],
        },
        "updates": {
            "version": "1.4",
            "main": {
                "badge": {"ja": "改善", "en": "Improved"},
                "title": {"ja": "人物登録の学歴と年齢が、より正確に", "en": "More accurate school years and ages for registered people"},
                "body": {
                    "ja": "人物の生まれ月を登録できるようになり、1〜3月生まれ（早生まれ）も含めて、高校・大学の入学・卒業や浪人の年を正しく計算するようになりました。年表の各年に登録した人の年齢を表示でき、満年齢と数え年を切り替えられます。履歴書に書く学歴の年や、家族の節目の年を調べるのがぐっと確実になります。",
                    "en": "You can now register a person's birth month, so high school and university entry and graduation years — and gap years — are calculated correctly, including for people born January to March (early-born in Japan's school year). The timeline can also show each registered person's age for every year, in Western or traditional (kazoe) counting. Looking up school years for a résumé or family milestones is now far more reliable.",
                },
                "steps": [],
                "note": {
                    "ja": "満年齢と数え年の違いは、設定の「人物・人生イベント」のヘルプでいつでも確認できます。4月1日生まれの方は前の学年になるため、メモで補足してください。",
                    "en": "The difference between Western and traditional counting is explained in the help under People & Life Events in Settings. People born on April 1 belong to the previous school year, so add a note for them.",
                },
            },
            "others": {
                "ja": [
                    "干支の表示をオン／オフでかんたんに切り替え、表示形式も選べるようになりました",
                    "一部の表示の不具合と、購入画面の移動に関する不具合を修正しました",
                ],
                "en": [
                    "Turn the zodiac display on or off easily, and choose its format",
                    "Fixed some display issues and a navigation issue on the purchase screen",
                ],
            },
        },
        "pricing": {"ja": ["基本無料（広告あり・1854年以降の年代）", "1か月 ¥100 / 1年 ¥200", "買い切り ¥500"],
                    "en": ["Free with ads (years from 1854 onward)", "¥100 / month, ¥200 / year", "Lifetime: ¥500"]},
    },
    {
        "slug": "pointonimage",
        "popular_note": {"ja": "直近3か月のダウンロード数で、川助商店のいちばん人気のアプリです。",
                         "en": "Our most downloaded app over the past three months."},
        "rank": 1,  # 直近3か月のダウンロード数の順位。サイトには順位だけ出す
        "top_plan": 2,  # 購入がいちばん多いプランの pricing の位置
        "id": "6792205062",
        "name": {"ja": "座標と色", "en": "Coord & Color"},
        "full": {"ja": "座標と色 - 画像のピクセル位置とカラー抽出", "en": "Coord & Color: Pixel Picker"},
        "tagline": {"ja": "画像の上の2点を、ピクセル単位で測る。",
                    "en": "Measure two points on an image, down to the pixel."},
        "category": {"ja": "開発ツール", "en": "Developer Tools"},
        "os": {"ja": "iOS 18.4 以降", "en": "iOS 18.4 or later"},
        "features": {
            "ja": [
                "画像をタップして2点を配置。拡大鏡でピクセル単位まで正確に指定",
                "X差・Y差・直線距離を自動計算。ピクセル値と0〜1の比率で表示",
                "座標・ΔX/ΔY・直線距離を数値やスライダーで指定して点を配置（複数の指で同時に微調整）",
                "原点(0, 0)を四隅のどこにでも設定",
                "色を取得してHEX・RGBで表示（長押しでコピー）",
                "指定した半径の円を描画",
                "十字線・円つきの画像や、座標パネルつきの画像を書き出して共有",
                "2枚目の画像を開き、1枚目と同じ座標で位置や色を比較（Pro）",
                "計測した画像と座標を最大10件まで保存・読み出し（Pro）",
            ],
            "en": [
                "Tap to place two points, with a magnifier for pixel-level precision",
                "Automatic ΔX, ΔY and straight-line distance, in pixels or 0–1 ratios",
                "Place points by entering coordinates, ΔX/ΔY or distance, or with sliders (fine-tune several at once with multiple fingers)",
                "Set the origin (0, 0) at any of the four corners",
                "Pick colors and read them as HEX and RGB (long-press to copy)",
                "Draw circles of a given radius",
                "Export and share the image with crosshairs and circles, or with the coordinate panel",
                "Open a second image and compare positions and colors at the same coordinates (Pro)",
                "Save up to 10 measured images with their points and load them anytime (Pro)",
            ],
        },
        "updates": {
            "version": "1.3",
            "main": {
                "badge": {"ja": "新機能", "en": "New"},
                "pro": {"ja": "Pro（有料版）の機能です。動画広告を見ると、3枚分お試しできます。",
                        "en": "This is a Pro (paid) feature. Watch a video ad to try it on 3 photos."},
                "title": {"ja": "2枚の画像を、同じ座標で見比べる", "en": "Compare two images at the same coordinates"},
                "body": {
                    "ja": "1枚目で計測したA・B点を残したまま、2枚目の画像を開いてC・D点を配置できるようになりました。2枚目には1枚目のA・B点が点線で重ねて表示され、「A・B点をコピー」を押せば、同じ座標にC・D点をすぐ置けます。撮り直した写真や同じ構図の別の画像で、位置や色がどう変わったのかを同じ基準で確かめられるのが嬉しいところです。",
                    "en": "You can now keep points A and B from your first image and open a second image to place points C and D. Points A and B from the first image appear as dotted lines on the second, and Copy Points A & B places C and D at the very same coordinates. Check how positions and colors changed between a retake or another shot with the same framing, using exactly the same reference.",
                },
                "steps": [
                    {"img": "screens/pointonimage-compare-1.jpg",
                     "ja": "1枚目の画像でA・B点を配置して計測",
                     "en": "Place points A and B on the first image and measure"},
                    {"img": "screens/pointonimage-compare-2.jpg",
                     "ja": "2枚目を開くと1枚目のA・B点が点線で表示。「A・B点をコピー」で同じ座標にC・D点を置き、「1枚目の画像」ボタンで2枚を切り替え",
                     "en": "On the second image, A and B appear as dotted lines. Tap Copy Points A & B to put C and D at the same coordinates, and switch images with the 1st Image button"},
                ],
                "note": {
                    "ja": "動画広告でお試しする場合、2枚を比較表示しても1枚としてカウントされます。",
                    "en": "When trying it with a video ad, comparing two images counts as one photo.",
                },
            },
            "extra": [
                {
                    "img": "screens/pointonimage-presets.jpg",
                    "badge": {"ja": "新機能", "en": "New"},
                    "pro": {"ja": "Pro（有料版）の機能です。", "en": "This is a Pro (paid) feature."},
                    "title": {"ja": "計測した画像と座標を保存して、あとで読み出す",
                              "en": "Save measured images with their points, and load them later"},
                    "body": {
                        "ja": "計測した画像とA・B点の座標（半径も含む）を、セットで最大10件まで保存できるようになりました。読み出した点はロックされた状態で配置されるので、うっかり動かしてしまう心配がありません。同じ箇所を何度も測る作業や、2枚目と比べるときの基準づくりがぐっと楽になります。",
                        "en": "Save up to 10 measured images together with the coordinates of points A and B (radius included). Loaded points are placed locked, so you won't move them by accident — handy when you measure the same spot repeatedly or need a fixed reference for comparing a second image.",
                    },
                    "points": {
                        "ja": [
                            "写真一覧の読み出しボタンや、2枚目の比較中から呼び出せる",
                            "一覧で保存日時とA・B点の座標をひと目で確認",
                            "「すべて選択」でまとめて削除",
                        ],
                        "en": [
                            "Load them from the photo list or while comparing a second image",
                            "See the save date and the coordinates of A and B at a glance",
                            "Delete several at once with Select All",
                        ],
                    },
                },
                {
                    "img": "screens/pointonimage-plot.jpg",
                    "badge": {"ja": "新機能", "en": "New"},
                    "title": {"ja": "座標を数値で指定して、点をぴたりと置く",
                              "en": "Enter coordinates to place points exactly"},
                    "body": {
                        "ja": "下のパネルの座標をタップすると「座標を指定して配置」が開き、A・B点のX・Yを数値で入力したり、スライダーや◀▶ボタンで少しずつ動かしたりできます。指で狙いにくい細かな位置でも、決めた座標に確実に点を置けます。",
                        "en": "Tap the coordinates in the bottom panel to open Plot Coordinates, then type X and Y for points A and B or nudge them with sliders and the ◀ ▶ buttons. Hit the exact coordinates you want, even where a fingertip can't aim precisely.",
                    },
                    "points": {
                        "ja": [
                            "入力できる範囲（画像のサイズ）を表示",
                            "相対位置の表示にしているときは0〜1で入力",
                            "複数の指で、いくつものスライダーを同時に操作できる",
                        ],
                        "en": [
                            "Shows the valid input range (the image size)",
                            "Enter values from 0 to 1 when relative positions are shown",
                            "Move several sliders at the same time with multiple fingers",
                        ],
                    },
                },
                {
                    "img": "screens/pointonimage-metric.jpg",
                    "badge": {"ja": "新機能", "en": "New"},
                    "title": {"ja": "ΔX・ΔY・直線距離を指定して、もう一方の点を動かす",
                              "en": "Set ΔX, ΔY or distance to move the other point"},
                    "body": {
                        "ja": "ΔX・ΔY・DIST（直線距離）をタップすると「差分・距離の指定」が開き、数値の入力とスライダーで調整できます。「右に1301px、下に898px」や「ちょうど1500px離す」のように、決まった間隔の位置へもう一方の点を置けます。",
                        "en": "Tap ΔX, ΔY or DIST to open Delta & Distance Settings and adjust them by typing or with sliders. Put the other point at a set offset — say 1301 px right and 898 px down, or exactly 1500 px away.",
                    },
                    "points": {
                        "ja": [
                            "点をロックしておけば、基準の点を動かさずに調整できる",
                            "スライダーと◀▶ボタンで細かく調整",
                        ],
                        "en": [
                            "Lock a point to keep your reference fixed while adjusting",
                            "Fine-tune with sliders and the ◀ ▶ buttons",
                        ],
                    },
                },
                {
                    "img": "screens/pointonimage-loupe.jpg",
                    "badge": {"ja": "無料に", "en": "Now free"},
                    "title": {"ja": "拡大鏡・原点の変更・相対位置表示などが無料に",
                              "en": "Magnifier, origin position, relative positions and more are now free"},
                    "body": {
                        "ja": "これまでPro機能だった拡大鏡、原点位置の変更、相対位置（0〜1）の表示、座標パネル込みの共有が、回数の制限なく無料で使えるようになりました。1ピクセル単位の位置合わせも、購入せずにそのまま試せます。",
                        "en": "The magnifier, changing the origin position, relative (0–1) positions and sharing with the coordinate panel used to be Pro features. They are now free with no usage limit, so pixel-perfect placement is available without a purchase.",
                    },
                    "points": {
                        "ja": [
                            "点の配置・微調整のときに拡大鏡を表示",
                            "原点(0, 0)は四隅のどこにでも設定できる",
                        ],
                        "en": [
                            "The magnifier appears while you place or fine-tune points",
                            "Put the origin (0, 0) in any of the four corners",
                        ],
                    },
                },
            ],
            "others": {
                "ja": [
                    "外観モード（システム設定に合わせる・ライト・ダーク）を選べるようになりました",
                    "Proを購入すると、写真一覧の広告が表示されなくなります",
                ],
                "en": [
                    "Choose the appearance: match the system, light or dark",
                    "Buying Pro removes the ad from the photo list",
                ],
            },
        },
        "pricing": {"ja": ["基本無料（広告あり・基本の計測は枚数制限なし）", "月額 ¥100 / 年額 ¥300", "買い切り ¥1,000"],
                    "en": ["Free with ads (core measuring, no image limit)", "¥100 / month, ¥300 / year", "Lifetime: ¥1,000"]},
    },
    {
        "slug": "fishing",
        "top_plan": 2,  # 購入がいちばん多いプランの pricing の位置
        "popular_note": {"ja": "2013年から続くロングセラー。有料版は今も、川助商店でいちばんよく選ばれているアプリのひとつです。",
                         "en": "A long-seller since 2013 — still one of our most purchased upgrades."},
        "id": "729354409",
        "name": {"ja": "釣り師の単位変換", "en": "Angler's Unit Converter"},
        "full": {"ja": "釣り師の単位変換", "en": "Angler's Unit Converter"},
        "tagline": {"ja": "釣りのややこしい単位を、すぐに変換。",
                    "en": "Convert confusing fishing units in an instant."},
        "category": {"ja": "スポーツ", "en": "Sports"},
        "os": {"ja": "iOS 18.0 以降（iPhone）", "en": "iOS 18.0 or later (iPhone)"},
        "features": {
            "ja": [
                "オモリ：号・oz・lb・g・貫・grain（フライライン用）を変換。ozは 1/16 のような分数でも入力可能",
                "ライン：PE（号）、ナイロン/フロロ（号）、lb、kg を変換。対象魚とサイズから道糸・ハリスの太さを提案",
                "長さ：m・cm・mm・ft・inch・yd・尺・寸・分・ヒロ・fathom などを変換",
                "ガン玉・スプリットショット・かみつぶしの早見表",
                "並べ替えやスワイプでの切り替え、入力内容の自動保存",
                "よく使う変換をお気に入りに保存（無料版は1件、プレミアムは30件まで・並べ替え可能）",
            ],
            "en": [
                "Sinkers: convert Japanese gō, oz, lb, g, kan and grain (for fly lines); enter oz as fractions like 1/16",
                "Line: convert PE (gō), nylon/fluorocarbon (gō), lb and kg; get main line and leader suggestions by target fish and size",
                "Length: m, cm, mm, ft, inch, yd, and traditional units such as shaku, sun and hiro, plus fathoms",
                "Quick reference charts for split shot and other small sinkers",
                "Reorder and swipe between tabs; inputs are saved automatically",
                "Save frequent conversions as favorites (1 free, up to 30 with Premium; reorderable)",
            ],
        },
        "pricing": {"ja": ["基本無料（広告あり・1日5回まで。動画広告を見ると＋10回、最大30回まで貯められる）", "プレミアム 1か月 ¥100 / 1年 ¥300", "買い切り ¥500"],
                    "en": ["Free with ads (5 conversions a day; watch a video ad for +10, store up to 30)", "Premium: ¥100 / month, ¥300 / year", "Lifetime: ¥500"]},
    },
    {
        "slug": "sanpai",
        "id": "6799005788",
        # お知らせ（不具合のお詫びなど）。解消したらこの項目を消す
        "notice": {
            "ja": "【お詫び】現在、Game Center のリーダーボードの設定に不備があり、「全国参拝数ランキング」をご利用いただけません。楽しみにしてくださっていた皆さまには、ご迷惑をおかけして申し訳ありません。復旧に向けて対応を進めており、使えるようになりましたらこのページでお知らせします。参拝の記録・御朱印の整理など、ほかの機能はこれまでどおりお使いいただけます。",
            "en": "Our apologies: due to a misconfiguration of the Game Center leaderboards, the nationwide visit-count ranking is currently unavailable. We are sorry for the inconvenience to everyone who was looking forward to it. We are working on a fix and will announce it on this page once the ranking is back. All other features, such as recording visits and organizing goshuin, work as usual.",
        },
        "name": {"ja": "参拝記録", "en": "Shrine Visit Log"},
        "full": {"ja": "参拝記録", "en": "Shrine Visit Log"},
        "tagline": {"ja": "自分だけの、静かな参拝の記録。",
                    "en": "A quiet, private record of your shrine visits."},
        "category": {"ja": "ライフスタイル", "en": "Lifestyle"},
        "os": {"ja": "iOS 18.0 以降", "en": "iOS 18.0 or later"},
        "features": {
            "ja": [
                "地図で近くの神社を探し、境内で参拝を記録",
                "神社ごとの写真や御朱印、メモをまとめて保存",
                "御朱印は朱印帳（冊）ごとに整理",
                "参拝の記録は端末とご自身のiCloudに保存",
                "Game Center の「全国参拝数ランキング」（参加は任意。※現在ご利用いただけません）",
            ],
            "en": [
                "Find nearby shrines on the map and record your visit on the grounds",
                "Keep photos, goshuin stamps and notes together for each shrine",
                "Organize goshuin by stamp book",
                "Your records are stored on your device and in your own iCloud",
                "Nationwide visit-count ranking on Game Center (optional; currently unavailable)",
            ],
        },
        "guide": [
            {
                "img": "screens/sanpai-map.jpg",
                "title": {"ja": "地図で、近くの神社を見つける", "en": "Find shrines near you on the map"},
                "body": {
                    "ja": "現在地のまわりの神社が、鳥居のピンで地図に並びます。大きな神社だけでなく、住宅地の小さな社まで表示されるので、いつもの散歩道や旅先で通り過ぎていた神社に気づけます。",
                    "en": "Shrines around you appear on the map as torii pins. Not just the famous ones — small neighborhood shrines show up too, so you notice the ones you used to walk right past.",
                },
                "points": {
                    "ja": [
                        "画面下のバーに、いちばん近い神社までの距離を表示",
                        "神社から50m以内に入ると「参拝記録」ボタンが押せるように",
                        "ピンの右下の紋は、稲荷・八幡などその神社の系統の目印",
                        "右上のボタンから「参拝済み」「御朱印あり」「お気に入り」「行きたい」などで絞り込み",
                    ],
                    "en": [
                        "The bar at the bottom shows the distance to the nearest shrine",
                        "Within 50 m of a shrine, the “Record visit” button becomes available",
                        "The crest at the corner of a pin marks the shrine’s tradition, such as Inari or Hachiman",
                        "Filter the map by visited, has goshuin, favorites or want to visit from the top-right button",
                    ],
                },
            },
            {
                "img": "screens/sanpai-trend.jpg",
                "title": {"ja": "参拝のペースを、グラフでふり返る", "en": "Look back on your visits in a chart"},
                "body": {
                    "ja": "「記録」タブでは、参拝の回数を日・週・月・年・全期間で切り替えてグラフにできます。旅行で多く巡った月や、しばらく足が遠のいていた時期がひと目でわかります。",
                    "en": "In the Records tab, chart your visits by day, week, month, year or all time. Busy travel months and quiet stretches stand out at a glance.",
                },
                "points": {
                    "ja": [
                        "今月と過去12か月の平均を並べて表示",
                        "「平均より何回多いか」を一文で教えてくれる",
                        "都道府県別の参拝履歴も地図で確認",
                    ],
                    "en": [
                        "This month shown next to your 12-month average",
                        "A one-line summary tells you how far above or below average you are",
                        "See your visits by prefecture on a map",
                    ],
                },
            },
            {
                "img": "screens/sanpai-stats.jpg",
                "title": {"ja": "これまでの歩みを、数字で", "en": "Your journey in numbers"},
                "body": {
                    "ja": "参拝した回数や神社の数、朱印帳や写真の枚数を一覧で確認できます。各項目をタップすると、その中身の一覧へ進めます。",
                    "en": "See how many times you have visited, how many shrines, and how many stamp books and photos you have — tap any row to see the details.",
                },
                "points": {
                    "ja": [
                        "参拝数・参拝した神社の数・連続参拝日数",
                        "朱印帳の冊数と、収めた御朱印の数",
                        "神社で撮った写真をまとめたアルバム",
                        "旧国（令制国）をいくつ巡ったかの達成率",
                    ],
                    "en": [
                        "Total visits, shrines visited and visit streak",
                        "Number of stamp books and the goshuin they hold",
                        "An album of the photos you took at shrines",
                        "How many of Japan's old provinces you have visited",
                    ],
                },
            },
            {
                "img": "screens/sanpai-lineage.jpg",
                "title": {"ja": "神社の系統ごとに、巡った足あと", "en": "Your visits by shrine tradition"},
                "body": {
                    "ja": "八幡・稲荷・諏訪・熊野など、神社をその系統ごとにまとめて数えます。それぞれの紋とともに並ぶので、自分がどんな神社に惹かれているのかが見えてきます。",
                    "en": "Shrines are grouped by tradition — Hachiman, Inari, Suwa, Kumano and more — each shown with its crest, so you can see which kinds of shrines draw you in.",
                },
                "points": {
                    "ja": [
                        "30を超える系統に対応",
                        "「参拝した神社の数」と「延べ参拝数」を切り替え",
                        "系統をタップすると、その神社だけに絞り込み",
                    ],
                    "en": [
                        "More than 30 traditions",
                        "Switch between shrines visited and total visits",
                        "Tap a tradition to see just those shrines",
                    ],
                },
            },
            {
                "img": "screens/sanpai-goshuin.jpg",
                "title": {"ja": "御朱印を、朱印帳ごとにきれいに残す", "en": "Keep your goshuin, book by book"},
                "body": {
                    "ja": "いただいた御朱印は、カメラで読み取ってアプリに保存できます。実物の朱印帳と同じように「1冊目」「2冊目」と分けて綴じておけるので、手元の朱印帳をそのまま持ち歩いているような感覚で見返せます。",
                    "en": "Scan the goshuin you receive with the camera and save them in the app. File them into “Book 1”, “Book 2” and so on, just like your real stamp books, and flip back through them anytime.",
                },
                "points": {
                    "ja": [
                        "書類スキャンで、ゆがみを補正してきれいに取り込み",
                        "神社名・所在地で検索、日付順や名前順に並べ替え",
                        "朱印帳に未登録の御朱印は、あとからまとめて整理",
                    ],
                    "en": [
                        "Document scanning straightens and crops each sheet cleanly",
                        "Search by shrine name or location; sort by date or name",
                        "Sort unfiled goshuin into books later, all at once",
                    ],
                },
            },
            {
                "img": "screens/sanpai-backup.jpg",
                "title": {"ja": "大切な記録を、二重に守る", "en": "Your records, backed up twice"},
                "body": {
                    "ja": "記録は端末の中とご自身のiCloudの両方に残せます。機種変更のときや、もしものときにも記録を取り戻せます。",
                    "en": "Keep your records both on your device and in your own iCloud, so you can get them back when you switch phones or if something goes wrong.",
                },
                "points": {
                    "ja": [
                        "記録の登録・編集のたびに、端末内へスナップショットを自動作成。直前から1か月前まで最大8件を保存",
                        "無料版は最新の1件、有料版は保存されたすべての時点から復元できる",
                        "復元の前に、戻る記録・消える記録・内容が変わる記録の件数を確認できる",
                        "iCloudへの自動バックアップ。朱印帳の画像も含められる",
                        "機種変更のときは、バックアップから復元",
                    ],
                    "en": [
                        "Each time you add or edit a record, a snapshot is created on your device automatically — up to 8 are kept, from the latest back to a month ago",
                        "Free: restore the latest snapshot. Paid: restore any saved snapshot",
                        "Before restoring, see how many records will come back, be removed or change",
                        "Automatic iCloud backup, optionally including your stamp book images",
                        "Restore from backup when you switch to a new iPhone",
                    ],
                },
            },
        ],
        "pricing": {"ja": ["基本無料（広告あり）", "月額 ¥100 / 年額 ¥800"],
                    "en": ["Free with ads", "¥100 / month, ¥800 / year"]},
    },
]

# ---------------------------------------------------------------- UI text

T = {
    "ja": {
        "store": "川助商店", "store_sub": "kawasuke store",
        "site_desc": "川助商店（kawasuke store）が開発・提供しているiPhoneアプリの紹介サイトです。",
        "nav_apps": "アプリ", "nav_privacy": "プライバシー", "nav_eula": "利用規約", "nav_contact": "お問い合わせ",
        "f_apps": "アプリ一覧", "f_privacy": "プライバシーポリシー", "f_eula": "利用規約（EULA）",
        "trademark": "iPhone、App Store は Apple Inc. の商標です。",
        "kamon_alt": "川助商店の家紋",
        "lead": '日々の小さな「ちょっと面倒」を片づける、<br class="pc">iPhoneアプリをつくっています。',
        "sub": '写真の整理や比較、暦の変換、釣りの単位まで。<br class="pc">一つひとつ、すっきりと使える道具を目指しています。',
        "menu": "品書き", "apps_title": "アプリ一覧", "soon": "近日公開",
        "dev_page": "App Store のデベロッパページを見る →",
        "privacy_h": "プライバシー",
        "privacy_p": '写真の解析や変換は、できるかぎり端末の中だけで行います。広告と課金で利用する外部サービスについては、<a href="{p}privacy.html">プライバシーポリシー</a>に記載しています。',
        "contact_h": "お問い合わせ",
        "contact_p": f'不具合のご報告やご要望は、<a href="{CONTACT_FORM}" target="_blank" rel="noopener">お問い合わせフォーム</a>からお寄せください。アプリ名と、お使いのiPhone・iOSのバージョンを添えていただけると助かります。',
        "appstore": "App Store で見る",
        "features": "主な機能", "pricing": "料金", "env": "対応環境", "legal": "規約とサポート",
        "price_note": "価格は日本のApp Storeのものです。最新の価格はApp Storeでご確認ください。サブスクリプションは自動更新です。解約はiPhoneの［設定］＞［Apple アカウント］＞［サブスクリプション］から行えます。",
        "back": "← アプリ一覧へ戻る",
        "guide": "画面の解説",
        "summary_title": "このアプリの良さをひとことで言うと", "needs_title": "こんなお悩みにおすすめ", "faq_title": "よくある質問",
        "updates": "アップデート情報",
        "updates_ver": "バージョン {v} の新しい点",
        "updates_others": "そのほかの改善",
        "rank": "人気 {n} 位",
        "rank_note": "王冠は、直近3か月のダウンロード数の順位です。",
        "top_plan": "いちばん人気",
        "about_label": "店主", "about_title": "つくっている人",
        "about_lead": "組込み機器と画像処理の開発に携わってきた店主が、釣りや寺社めぐりの中で「あったら便利」と感じた道具を、2013年からひとりで形にしているiPhoneアプリの店です。",
        "updated": "最終改定日：",
        "nf_title": "ページが見つかりません", "nf_body": "お探しのページは移動または削除された可能性があります。", "nf_home": "トップページへ",
    },
    "en": {
        "store": "Kawasuke Store", "store_sub": "川助商店",
        "site_desc": "Kawasuke Store (川助商店) makes small, focused iPhone apps.",
        "nav_apps": "Apps", "nav_privacy": "Privacy", "nav_eula": "Terms", "nav_contact": "Contact",
        "f_apps": "All apps", "f_privacy": "Privacy Policy", "f_eula": "Terms of Use (EULA)",
        "trademark": "iPhone and App Store are trademarks of Apple Inc.",
        "kamon_alt": "Kawasuke Store family crest",
        "lead": 'Small iPhone apps that take care of<br class="pc"> everyday little hassles.',
        "sub": 'From sorting and comparing photos to calendar and fishing-unit conversion —<br class="pc"> each one built to be simple and clean to use.',
        "menu": "Menu", "apps_title": "Apps", "soon": "Coming soon",
        "dev_page": "See all apps on the App Store →",
        "privacy_h": "Privacy",
        "privacy_p": 'Photos are analyzed and converted on your device whenever possible. The third-party services used for ads and purchases are described in our <a href="{p}privacy.html">Privacy Policy</a>.',
        "contact_h": "Contact",
        "contact_p": f'For bug reports or requests, please use the <a href="{CONTACT_FORM}" target="_blank" rel="noopener">contact form</a>. Including the app name and your iPhone and iOS version helps a lot.',
        "appstore": "View on the App Store",
        "features": "Features", "pricing": "Pricing", "env": "Requirements", "legal": "Legal & support",
        "price_note": "Prices are for the Japanese App Store and may differ in your region; check the App Store for current prices. Subscriptions renew automatically. Cancel anytime in Settings > Apple Account > Subscriptions.",
        "back": "← Back to all apps",
        "guide": "A closer look",
        "summary_title": "What makes this app great, in a nutshell", "needs_title": "Made for moments like these", "faq_title": "Frequently asked questions",
        "updates": "What's new",
        "updates_ver": "New in version {v}",
        "updates_others": "Other improvements",
        "rank": "Top {n}",
        "rank_note": "Crowns mark our most downloaded apps over the past three months.",
        "top_plan": "Most popular",
        "about_label": "Maker", "about_title": "Who makes these apps",
        "about_lead": "A one-person iPhone app shop, run since 2013 by a developer with a background in embedded systems and image processing, building the small tools that would have come in handy while fishing or visiting shrines and temples.",
        "updated": "Last updated: ",
        "nf_title": "Page not found", "nf_body": "The page you are looking for may have been moved or removed.", "nf_home": "Go to home page",
    },
}

LANGS = ("ja", "en")


def out_dir(lang):
    return OUT if lang == "ja" else OUT / "en"


def appstore_url(app, lang):
    if not app["id"]:
        return None
    return f"https://apps.apple.com/{'jp/' if lang == 'ja' else ''}app/id{app['id']}"


# ---------------------------------------------------------------- layout

def page(lang, rel_path, title, body, *, description="", active="", absolute=False,
         content_lang=None, head_extra="", og_image="og-default.png"):
    """rel_path: 言語ルートからの相対パス（例 "apps/picdiff.html"）。
    content_lang: 日英以外の言語ページ（/<言語>/apps/...）を作るときの言語。ヘッダー等は英語（lang="en"）で出す。"""
    t = T[lang]
    depth = rel_path.count("/") + (1 if lang == "en" else 0)
    r = "../" * depth                       # サイトのルート（assets 用）
    p = "../" * rel_path.count("/")         # 言語ルート（ページ間リンク用）
    other = "en" if lang == "ja" else "ja"
    if lang == "ja":
        other_href = r + "en/" + rel_path
    else:
        other_href = r + rel_path
    if content_lang:  # /<言語>/apps/... … サイト内リンクは英語版へ
        p = r + "en/"
        other_href = r + rel_path
    if absolute:  # 404 はどの階層でも表示されるので、絶対パスでリンクする
        r = "/"
        p = "/" if lang == "ja" else "/en/"
        other_href = ("/en/" if lang == "ja" else "/") + rel_path
    full_title = f"{title} | {t['store']}" if title else f"{t['store']} {t['store_sub']}"
    desc = escape(description or t["site_desc"])

    def nav(href, label, key):
        cur = ' aria-current="page"' if key == active else ""
        return f'<a href="{p}{href}"{cur}>{label}</a>'

    if content_lang:
        switch = (f'<a href="{other_href}" lang="ja" hreflang="ja">日本語</a>'
                  f'<a href="{r}en/{rel_path}" lang="en" hreflang="en">English</a>')
    elif lang == "ja":
        switch = f'<span lang="ja">日本語</span><a href="{other_href}" lang="en" hreflang="en">English</a>'
    else:
        switch = f'<a href="{other_href}" lang="ja" hreflang="ja">日本語</a><span lang="en">English</span>'

    return f"""<!DOCTYPE html>
<html lang="{content_lang or lang}">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<meta name="google-site-verification" content="LvHDKVz8nkrVXeBr2uE1J3WapKCn1XNOWXGnDK0vF10">
<title>{escape(full_title)}</title>
<meta name="description" content="{desc}">
<meta property="og:title" content="{escape(full_title)}">
<meta property="og:description" content="{desc}">
<meta property="og:type" content="website">
<meta property="og:locale" content="{'ja_JP' if lang == 'ja' else 'en_US'}">
<meta property="og:site_name" content="川助商店 kawasuke store">
<meta property="og:image" content="{SITE}/assets/og/{og_image}">
<meta property="og:image:width" content="1200">
<meta property="og:image:height" content="630">
<meta property="og:image:alt" content="{escape(full_title)}">
<meta name="twitter:card" content="summary_large_image">
<meta name="twitter:image" content="{SITE}/assets/og/{og_image}">
<link rel="alternate" hreflang="{other}" href="{other_href}">{head_extra}
<link rel="icon" href="{r}favicon.png" type="image/png">
<link rel="apple-touch-icon" href="{r}apple-touch-icon.png">
<link rel="stylesheet" href="{r}assets/style.css">
<script>
/* 初回訪問時だけ、ブラウザの言語に合わせて日本語/英語へ自動で振り分ける。
   どちらかを手動で選んだら、その選択を優先する。 */
(function () {{
  var LANG = "{lang}", OTHER = "{other_href}";
  try {{
    var saved = localStorage.getItem("lang");
    if (!saved) {{
      var nav = (navigator.languages && navigator.languages[0]) || navigator.language || "";
      var want = /^ja/i.test(nav) ? "ja" : "en";
      localStorage.setItem("lang", want);
      if (want !== LANG) location.replace(OTHER);
    }}
  }} catch (e) {{}}
  document.addEventListener("click", function (e) {{
    var a = e.target.closest && e.target.closest(".lang-switch a");
    if (a) {{ try {{ localStorage.setItem("lang", a.getAttribute("hreflang")); }} catch (_) {{}} }}
  }});
}})();
</script>
</head>
<body>
<header class="site-header">
  <div class="wrap header-inner">
    <a class="brand" href="{p}index.html">
      <img src="{r}assets/kamon.png" alt="" width="40" height="40">
      <span class="brand-text"><span class="brand-ja">{t['store']}</span><span class="brand-en">{t['store_sub']}</span></span>
    </a>
    <nav class="site-nav">
      {nav("index.html#apps", t['nav_apps'], "apps")}
      {nav("privacy.html", t['nav_privacy'], "privacy")}
      {nav("eula.html", t['nav_eula'], "eula")}
      <a href="{CONTACT_FORM}" target="_blank" rel="noopener">{t['nav_contact']}</a>
      <span class="lang-switch">{switch}</span>
    </nav>
  </div>
</header>
<main>
{body}
</main>
<footer class="site-footer">
  <div class="wrap footer-inner">
    <div class="footer-brand">
      <img src="{r}assets/kamon.png" alt="" width="32" height="32">
      <span>{t['store']}</span>
    </div>
    <nav class="footer-nav">
      <a href="{p}index.html#apps">{t['f_apps']}</a>
      <a href="{p}privacy.html">{t['f_privacy']}</a>
      <a href="{p}eula.html">{t['f_eula']}</a>
      <a href="{CONTACT_FORM}" target="_blank" rel="noopener">{t['nav_contact']}</a>
    </nav>
    <p class="copyright">© 2013–2026 川助商店 (kawasuke store)<br>{t['trademark']}</p>
  </div>
</footer>
<!-- Cloudflare Web Analytics --><script type="module" src="https://static.cloudflareinsights.com/beacon.min.js" data-cf-beacon='{{"token": "{CF_ANALYTICS_TOKEN}"}}'></script><!-- End Cloudflare Web Analytics -->
</body>
</html>
"""


def write(lang, rel_path, html):
    path = out_dir(lang) / rel_path
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(html, encoding="utf-8")


def appstore_button(url, lang):
    t = T[lang]
    if not url:
        return f'<span class="btn btn-disabled">{t["soon"]}</span>'
    return (f'<a class="btn btn-primary" href="{url}" target="_blank" rel="noopener">'
            '<svg viewBox="0 0 24 24" width="18" height="18" aria-hidden="true"><path fill="currentColor" d="M16.4 12.6c0-2.4 2-3.6 2.1-3.7-1.1-1.7-2.9-1.9-3.5-1.9-1.5-.2-2.9.9-3.7.9-.8 0-1.9-.9-3.2-.8-1.6 0-3.1 1-4 2.4-1.7 3-.4 7.3 1.2 9.7.8 1.2 1.8 2.5 3 2.4 1.2 0 1.7-.8 3.1-.8 1.5 0 1.9.8 3.2.8 1.3 0 2.1-1.2 2.9-2.4.9-1.4 1.3-2.7 1.3-2.8 0 0-2.4-.9-2.4-3.8zM14 5.4c.7-.8 1.1-1.9 1-3-.9 0-2.1.6-2.8 1.4-.6.7-1.2 1.9-1 2.9 1.1.1 2.1-.5 2.8-1.3z"/></svg>'
            f'{t["appstore"]}</a>')


# ---------------------------------------------------------------- pages

CROWN = ('<svg viewBox="0 0 24 24" width="14" height="14" aria-hidden="true"><path fill="currentColor" '
         'd="M3 7.5 7.5 11 12 4l4.5 7L21 7.5 19 18H5L3 7.5zM5 19.5h14V21H5z"/></svg>')


def rank_badge(a, lang):
    n = a.get("rank")
    if not n:
        return ""
    return f'<span class="rank rank-{n}">{CROWN}{T[lang]["rank"].format(n=n)}</span>'


# 直近3か月のダウンロード数の順（4位以下の並び順に使う。数値はサイトに出さない）
DL_ORDER = ["fishing", "heifconvert", "gengoseireki", "sanpai"]


def build_index(lang):
    t = T[lang]
    r = "" if lang == "ja" else "../"
    cards = []
    # 王冠つき（rank）の後は、直近3か月のダウンロード数の多い順。公開前のアプリは最後
    ordered = sorted(APPS, key=lambda a: a.get("rank") or (3 + DL_ORDER.index(a["slug"]) + 1 if a["slug"] in DL_ORDER else 99))
    for a in ordered:
        badge = "" if a["id"] else f'<span class="badge">{t["soon"]}</span>'
        cards.append(f"""
    <a class="app-card" href="apps/{a['slug']}.html">
      <img class="app-icon" src="{r}assets/icons/{a['slug']}.png" alt="" width="88" height="88" loading="lazy">
      <div class="app-card-body">
        <div class="app-card-meta">{escape(a['category'][lang])}{badge}{rank_badge(a, lang)}</div>
        <h3>{escape(a['name'][lang])}</h3>
        <p>{escape(a['tagline'][lang])}</p>
      </div>
    </a>""")
    body = f"""
<section class="hero">
  <div class="wrap hero-inner">
    <img class="hero-kamon" src="{r}assets/kamon.png" alt="{t['kamon_alt']}" width="220" height="220">
    <div class="hero-text">
      <p class="eyebrow">{t['store_sub']}</p>
      <h1>{t['store']}</h1>
      <p class="lead">{t['lead']}</p>
      <p class="sub">{t['sub']}</p>
    </div>
  </div>
</section>

<section class="section" id="apps">
  <div class="wrap">
    <h2 class="section-title"><span>{t['menu']}</span>{t['apps_title']}</h2>
    <p class="rank-note">{CROWN}{t['rank_note']}</p>
    <div class="app-grid">{''.join(cards)}
    </div>
    <p class="more"><a href="{DEVELOPER_PAGE[lang]}" target="_blank" rel="noopener">{t['dev_page']}</a></p>
  </div>
</section>

<section class="section section-muted">
  <div class="wrap notes">
    <div class="note">
      <h3>{t['privacy_h']}</h3>
      <p>{t['privacy_p'].format(p="")}</p>
    </div>
    <div class="note">
      <h3>{t['contact_h']}</h3>
      <p>{t['contact_p']}</p>
    </div>
  </div>
</section>
"""
    write(lang, "index.html", page(lang, "index.html", "", body, active="apps"))


def explainer_html(a, lang):
    """形式のちがいなどを、図（棒グラフ）と表で説明する欄。主な機能の下に出す。"""
    x = a.get("explainer")
    if not x or lang not in x["title"]:
        return ""
    bars = "".join(f"""
        <div class="ex-bar-row">
          <span class="ex-bar-label">{escape(b['label'])}</span>
          <span class="ex-bar-track"><span class="ex-bar ex-bar-{i}" style="width:{b['pct']}%"></span></span>
          <span class="ex-bar-note">{escape(b['note'][lang])}</span>
        </div>""" for i, b in enumerate(x["bars"]))
    head = "".join(f"<th scope=\"col\">{escape(h)}</th>" for h in x["head"][lang])
    rows = "".join("<tr><th scope=\"row\">" + escape(rw[0]) + "</th>" + "".join(f"<td>{escape(c)}</td>" for c in rw[1:]) + "</tr>"
                   for rw in x["rows"][lang])
    srcs = "".join(f"""<li><a href="{src['url'][lang]}" target="_blank" rel="noopener">{escape(src['title'][lang])}</a><br>{escape(src['note'][lang])}</li>"""
                   for src in x["sources"])
    src_label = "出典" if lang == "ja" else "Sources"
    return f"""
      <div class="explainer">
        <h2 class="section-title small">{escape(x['title'][lang])}</h2>
        <p>{escape(x['lead'][lang])}</p>
        <figure class="ex-bars">{bars}
          <figcaption>{escape(x['bar_caption'][lang])}</figcaption>
        </figure>
        <div class="ex-table-wrap">
          <table class="ex-table"><thead><tr>{head}</tr></thead><tbody>{rows}</tbody></table>
        </div>
        <p class="ex-tip">{escape(x['tip'][lang])}</p>
        <div class="ex-sources"><p>{src_label}</p><ul>{srcs}</ul></div>
      </div>"""


def updates_html(a, lang, r):
    u = a.get("updates")
    if not u:
        return ""
    t = T[lang]
    m = u["main"]
    steps = "".join(f"""
        <li class="update-step">
          <figure class="phone phone-sm"><img src="{r}assets/{st['img']}" alt="" loading="lazy"></figure>
          <p><span class="update-num">{i + 1}</span>{escape(st[lang])}</p>
        </li>""" for i, st in enumerate(m["steps"]))
    others = "".join(f"<li>{escape(x)}</li>" for x in u["others"][lang])
    extras = ""
    for x in u.get("extra", []):
        pts = "".join(f"<li>{escape(p)}</li>" for p in x["points"][lang])
        pro_badge = '<span class="update-badge update-badge-pro">Pro</span>' if x.get("pro") else ""
        pro_note = f' <strong class="update-pro-note">{escape(x["pro"][lang])}</strong>' if x.get("pro") else ""
        extras += f"""
    <div class="update-main update-extra">
      <figure class="phone phone-sm"><img src="{r}assets/{x['img']}" alt="" loading="lazy"></figure>
      <div>
        <p class="update-badges"><span class="update-badge">{escape(x['badge'][lang])}</span>{pro_badge}</p>
        <h3>{escape(x['title'][lang])}</h3>
        <p class="update-body">{escape(x['body'][lang])}{pro_note}</p>
        <ul class="check-list">{pts}</ul>
      </div>
    </div>"""
    return f"""
<section class="section updates" id="updates">
  <div class="wrap">
    <h2 class="section-title"><span>{t['updates']}</span>{t['updates_ver'].format(v=u['version'])}</h2>
    <div class="update-main">
      <p class="update-badges"><span class="update-badge">{escape(m['badge'][lang])}</span>{'<span class="update-badge update-badge-pro">Pro</span>' if m.get('pro') else ''}</p>
      <h3>{escape(m['title'][lang])}</h3>
      <p class="update-body">{escape(m['body'][lang])}{(' <strong class="update-pro-note">' + escape(m['pro'][lang]) + '</strong>') if m.get('pro') else ''}</p>
      <ol class="update-steps">{steps}
      </ol>
      <p class="fine">{escape(m['note'][lang])}</p>
    </div>{extras}
    <h3 class="update-others-title">{t['updates_others']}</h3>
    <ul class="check-list">{others}</ul>
  </div>
</section>
"""


def guide_html(a, lang, r):
    steps = a.get("guide") or []
    if not steps:
        return ""
    blocks = []
    for i, g in enumerate(steps):
        pts = "".join(f"<li>{escape(x)}</li>" for x in g["points"][lang])
        blocks.append(f"""
    <div class="guide-step{' reverse' if i % 2 else ''}">
      <figure class="phone"><img src="{r}assets/{g['img']}" alt="{escape(g['title'][lang])}" loading="lazy"></figure>
      <div class="guide-text">
        <p class="guide-num">{i + 1:02d}</p>
        <h3>{escape(g['title'][lang])}</h3>
        <p>{escape(g['body'][lang])}</p>
        <ul class="check-list">{pts}</ul>
      </div>
    </div>""")
    return f"""
<section class="section section-muted guide">
  <div class="wrap">
    <h2 class="section-title">{T[lang]['guide']}</h2>{''.join(blocks)}
  </div>
</section>
"""


# 利用規約に「アプリ別の補足」があるアプリは、その見出しへ直接リンクする
EULA_ANCHOR = {"sanpai": "#app-sanpai", "findsimilarpics": "#app-photos",
               "heifconvert": "#app-photos", "fishing": "#app-fishing"}


# ---------------------------------------------------------------- アプリページ専用の多言語化
# i18n/<slug>.json があるアプリだけ、ページ内に日英以外の言語の中身も持たせ、
# 「主な機能」の右上の切り替えで表示言語を変えられるようにする（サイト共通部分は日本語/英語のまま）。
CONTENT_LANG_ORDER = ["ja", "en", "es", "de", "fr", "pt", "ko", "zh-Hans", "zh-Hant"]
CONTENT_LANG_LABEL = {"ja": "日本語", "en": "English"}
TOP_PLAN_LABEL = {"es": "La más elegida", "de": "Am beliebtesten", "fr": "La plus choisie", "pt": "A mais escolhida",
                  "ko": "가장 인기", "zh-Hans": "最受欢迎", "zh-Hant": "最受歡迎"}
GLOBE = ('<svg viewBox="0 0 24 24" width="16" height="16" aria-hidden="true"><path fill="none" stroke="currentColor" stroke-width="1.6" '
         'd="M12 3a9 9 0 1 0 0 18 9 9 0 0 0 0-18Zm-8.5 9h17M12 3c2.5 2.6 3.8 5.6 3.8 9s-1.3 6.4-3.8 9c-2.5-2.6-3.8-5.6-3.8-9S9.5 5.6 12 3Z"/></svg>')


def load_content_langs(a):
    """i18n/<slug>.json の訳を、APPS の各項目と T に言語キーとして差し込む。対応言語の一覧を返す。"""
    path = ROOT / "i18n" / f"{a['slug']}.json"
    if not path.exists():
        return []
    import json
    data = json.loads(path.read_text(encoding="utf-8"))
    for lg, d in data.items():
        CONTENT_LANG_LABEL[lg] = d["label"]
        for k in ("full", "tagline", "category", "os", "popular_note", "features", "pricing"):
            if k in a and k in d:
                a[k][lg] = d[k]
        u = a.get("updates")
        if u and "updates" in d:
            du, m = d["updates"], u["main"]
            for k in ("badge", "title", "body", "note", "pro"):
                if k in m and k in du:
                    m[k][lg] = du[k]
            for st, txt in zip(m["steps"], du["steps"]):
                st[lg] = txt
            u["others"][lg] = du["others"]
            for x, dx in zip(u.get("extra", []), du.get("extra", [])):
                for k in ("badge", "pro", "title", "body", "points"):
                    if k in x and k in dx:
                        x[k][lg] = dx[k]
        for g, dg in zip(a.get("guide", []), d.get("guide", [])):
            for k in ("title", "body", "points"):
                g[k][lg] = dg[k]
        T[lg] = dict(T["en"], **d["T"], top_plan=TOP_PLAN_LABEL.get(lg, T["en"]["top_plan"]))
    return [lg for lg in CONTENT_LANG_ORDER if lg in ("ja", "en") or lg in data]


def load_llmo(a):
    """i18n/<slug>.llmo.json（要約・おすすめ・よくある質問。日英を含む全言語）を読み込む。
    AI検索（ChatGPT・Perplexity など）がアプリを紹介しやすくするための内容。
    ※類似写真検索は顔・人物を認識しない。「人を見分けて仕分ける」と読める表現は書かない。"""
    path = ROOT / "i18n" / f"{a['slug']}.llmo.json"
    if not path.exists():
        return
    data = json.loads(path.read_text(encoding="utf-8"))
    a["llmo"] = data
    for lg, d in data.items():
        if lg in T:
            T[lg].update(d.get("T", {}))


def _strong(text):
    """**太字** だけを <strong> にする"""
    return re.sub(r"\*\*(.+?)\*\*", r"<strong>\1</strong>", escape(text))


def _plain(text):
    return text.replace("**", "")


def summary_html(a, lang):
    d = (a.get("llmo") or {}).get(lang)
    if not d:
        return ""
    tags = "".join(f"<span>{escape(x)}</span>" for x in d["tags"])
    return (f'\n      <div class="tldr"><h2>{escape(T[lang]["summary_title"])}</h2>'
            f'<p>{_strong(d["summary"])}</p><div class="tldr-tags">{tags}</div></div>')


def needs_html(a, lang):
    d = (a.get("llmo") or {}).get(lang)
    if not d:
        return ""
    cards = "".join(f'\n      <div class="need"><h3>{escape(h)}</h3><p>{escape(b)}</p><p class="need-how">→ {escape(how)}</p></div>'
                    for h, b, how in d["needs"])
    return f"""
<section class="section needs-section">
  <div class="wrap">
    <h2 class="section-title">{escape(T[lang]['needs_title'])}</h2>
    <div class="needs">{cards}
    </div>
  </div>
</section>"""


def faq_html(a, lang):
    d = (a.get("llmo") or {}).get(lang)
    if not d:
        return ""
    items = "".join(f'\n    <details{" open" if i == 0 else ""}><summary>{escape(q)}</summary><p>{escape(ans)}</p></details>'
                    for i, (q, ans) in enumerate(d["faq"]))
    return f"""
<section class="section faq-section">
  <div class="wrap faq">
    <h2 class="section-title">{escape(T[lang]['faq_title'])}</h2>{items}
  </div>
</section>"""


SCHEMA_CATEGORY = {"Photo & Video": "MultimediaApplication", "Graphics & Design": "DesignApplication",
                   "Utilities": "UtilitiesApplication", "Developer Tools": "DeveloperApplication",
                   "Sports": "SportsApplication", "Lifestyle": "LifestyleApplication"}


def page_url(slug, lg):
    """拡張子なしの公開URL（Cloudflare は .html を外したURLへ転送する）"""
    return SITE + content_url(slug, lg).removesuffix(".html")


def app_jsonld(a, lg):
    """構造化データ（SoftwareApplication と、あれば FAQPage）"""
    name = a["full"][lg].split(" – ")[0].split(" - ")[0]
    alt = sorted({v for v in a["name"].values() if v != name})
    llmo = (a.get("llmo") or {}).get(lg)
    app = {
        "@context": "https://schema.org",
        "@type": "SoftwareApplication",
        "name": name,
        "url": page_url(a["slug"], lg),
        "inLanguage": lg,
        "description": _plain(llmo["summary"]) if llmo else a["tagline"][lg],
        "applicationCategory": SCHEMA_CATEGORY.get(a["category"]["en"], "UtilitiesApplication"),
        "operatingSystem": a["os"][lg],
        "featureList": a["features"][lg],
        "author": {"@type": "Organization", "name": "川助商店 (kawasuke store)", "url": SITE + "/"},
    }
    if alt:
        app["alternateName"] = alt
    store = appstore_url(a, "ja" if lg == "ja" else "en")
    if store:
        app["downloadUrl"] = app["installUrl"] = store
    if "無料" in a["pricing"]["ja"][0]:
        app["offers"] = {"@type": "Offer", "price": "0", "priceCurrency": "JPY"}
    blocks = [app]
    if llmo:
        blocks.append({
            "@context": "https://schema.org",
            "@type": "FAQPage",
            "inLanguage": lg,
            "mainEntity": [{"@type": "Question", "name": q, "acceptedAnswer": {"@type": "Answer", "text": ans}}
                           for q, ans in llmo["faq"]],
        })
    return "".join('\n<script type="application/ld+json">' + json.dumps(b, ensure_ascii=False).replace("</", "<\\/") + "</script>"
                   for b in blocks)


def content_url(slug, lg):
    """各言語のアプリページの絶対パス"""
    return f"/apps/{slug}.html" if lg == "ja" else f"/{lg}/apps/{slug}.html"


def content_switcher(langs, current, slug):
    opts = "".join(
        f'<option value="{content_url(slug, lg)}" data-lang="{lg}"{" selected" if lg == current else ""}>'
        f'{escape(CONTENT_LANG_LABEL[lg])}</option>' for lg in langs)
    return (f'<label class="content-lang">{GLOBE}<span class="sr-only">Language</span>'
            f'<select data-content-lang aria-label="Language">{opts}</select></label>')


def content_lang_script(slug, current, langs):
    """選んだ言語のURLへ移動する。初めて開いたときだけ、ブラウザの言語のページへ自動で移る。"""
    urls = {lg: content_url(slug, lg) for lg in langs}
    import json
    return f"""
<script>
(function () {{
  var KEY = "content-lang:{slug}", CURRENT = "{current}", URLS = {json.dumps(urls)};
  var sel = document.querySelector("select[data-content-lang]");
  if (sel) sel.addEventListener("change", function () {{
    var lg = sel.options[sel.selectedIndex].getAttribute("data-lang");
    try {{ localStorage.setItem(KEY, lg); }} catch (e) {{}}
    location.href = sel.value;
  }});
  var saved = null;
  try {{ saved = localStorage.getItem(KEY); }} catch (e) {{}}
  if (!saved && (CURRENT === "ja" || CURRENT === "en")) {{
    var nav = (navigator.languages && navigator.languages[0]) || navigator.language || "";
    var map = [[/^zh-(hant|tw|hk|mo)/i, "zh-Hant"], [/^zh/i, "zh-Hans"], [/^es/i, "es"], [/^de/i, "de"],
               [/^fr/i, "fr"], [/^pt/i, "pt"], [/^ko/i, "ko"]];
    for (var i = 0; i < map.length; i++) {{
      if (map[i][0].test(nav) && URLS[map[i][1]]) {{
        try {{ localStorage.setItem(KEY, map[i][1]); }} catch (e) {{}}
        location.replace(URLS[map[i][1]]); return;
      }}
    }}
  }}
  try {{ localStorage.setItem(KEY, CURRENT); }} catch (e) {{}}
}})();
</script>
"""


def app_content(a, lang, r, langs=None):
    """アプリページの中身（ヒーロー〜画面の解説）。lang は中身の言語。"""
    t = T[lang]
    feats = "".join(f"<li>{escape(f)}</li>" for f in a["features"][lang])
    top = a.get("top_plan")
    price = "".join(
        f'<li>{escape(p)}<span class="plan-tag">{t["top_plan"]}</span></li>' if i == top else f"<li>{escape(p)}</li>"
        for i, p in enumerate(a["pricing"][lang]))
    notice = f'<p class="app-notice" role="status">{escape(a["notice"][lang])}</p>' if lang in a.get("notice", {}) else ""
    pop = f'<p class="popular-note">{escape(a["popular_note"][lang])}</p>' if a.get("popular_note") else ""
    # 規約・ポリシーは日本語版と英語版のみ。日英以外の言語では英語版へリンクする
    legal_root = "/" if lang == "ja" else "/en/"
    switcher = content_switcher(langs, lang, a["slug"]) if langs else ""
    return f"""
<section class="app-hero">
  <div class="wrap app-hero-inner">
    <img class="app-icon app-icon-lg" src="{r}assets/icons/{a['slug']}.png" alt="" width="128" height="128">
    <div>
      <p class="eyebrow">{escape(a['category'][lang])} {rank_badge(a, lang)}</p>
      <h1>{escape(a['full'][lang])}</h1>
      <p class="lead">{escape(a['tagline'][lang])}</p>{pop}{notice}{summary_html(a, lang)}
      <div class="actions">{appstore_button(appstore_url(a, lang), lang)}</div>
    </div>
  </div>
</section>

<section class="section">
  <div class="wrap app-detail">
    <div>
      <div class="feature-head">
        <h2 class="section-title small">{t['features']}</h2>{switcher}
      </div>
      <ul class="feature-list">{feats}</ul>{explainer_html(a, lang)}
    </div>
    <aside class="spec">
      <h2 class="section-title small">{t['pricing']}</h2>
      <ul class="plain">{price}</ul>
      <p class="fine">{t['price_note']}</p>
      <h2 class="section-title small">{t['env']}</h2>
      <ul class="plain"><li>{escape(a['os'][lang])}</li></ul>
      <h2 class="section-title small">{t['legal']}</h2>
      <ul class="plain links">
        <li><a href="{legal_root}privacy.html">{t['f_privacy']}</a></li>
        <li><a href="{legal_root}eula.html{EULA_ANCHOR.get(a['slug'], '')}">{t['f_eula']}</a></li>
        <li><a href="{CONTACT_FORM}" target="_blank" rel="noopener">{t['nav_contact']}</a></li>
      </ul>
    </aside>
  </div>
</section>

{needs_html(a, lang)}
{updates_html(a, lang, r)}
{guide_html(a, lang, r)}
{faq_html(a, lang)}"""


def build_app(lang, a):
    langs = a.get("_content_langs") or []
    _write_app_page(lang, a, langs, lang)
    # 日英以外の言語ページは、英語版を作るときに一緒に出力する（/<言語>/apps/<slug>.html）
    if lang == "en":
        for lg in langs:
            if lg not in ("ja", "en"):
                _write_app_page("en", a, langs, lg)


def _write_app_page(site_lang, a, langs, clang):
    t = T[site_lang]
    rel = f"apps/{a['slug']}.html"
    r = "../" if site_lang == "ja" and clang == "ja" else "../../"
    body = f"""{app_content(a, clang, r, langs)}
{content_lang_script(a["slug"], clang, langs) if langs else ""}
<section class="section">
  <div class="wrap">
    <p class="back"><a href="{'../' if clang == 'ja' else '/en/'}index.html#apps">{T[clang]['back']}</a></p>
  </div>
</section>
"""
    head_extra = "".join(f'\n<link rel="alternate" hreflang="{lg}" href="{content_url(a["slug"], lg)}">'
                         for lg in langs if lg not in ("ja", "en"))
    head_extra += f'\n<link rel="canonical" href="{page_url(a["slug"], clang)}">' + app_jsonld(a, clang)
    extra = clang not in ("ja", "en")
    html = page(site_lang, rel, a["full"][clang].split(" – ")[0].split(" - ")[0] if extra else a["name"][site_lang], body,
                description=f"{a['full'][clang]}: {a['tagline'][clang]}",
                content_lang=clang if extra else None, head_extra=head_extra, og_image=f"og-{a['slug']}.png")
    path = (OUT / clang / rel) if extra else (out_dir(site_lang) / rel)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(html, encoding="utf-8")


def legal_page(lang, rel, title, inner, active):
    body = f"""
<section class="section">
  <div class="wrap legal">
    <h1>{title}</h1>
    <p class="updated">{T[lang]['updated']}{UPDATED[lang]}</p>
{inner}
  </div>
</section>
"""
    write(lang, rel, page(lang, rel, title, body, active=active))


def build_privacy():
    names_ja = "、".join(f"「{a['name']['ja']}」" for a in APPS)
    names_en = ", ".join(a["name"]["en"] for a in APPS)
    form_ja = f'<a href="{CONTACT_FORM}" target="_blank" rel="noopener">お問い合わせフォーム</a>'
    form_en = f'<a href="{CONTACT_FORM}" target="_blank" rel="noopener">contact form</a>'

    ja = f"""
<p>川助商店（以下「当方」）は、当方が提供するiOSアプリ（{names_ja}。以下まとめて「本アプリ」）における利用者の情報の取り扱いについて、以下のとおり定めます。</p>

<h2>1. 当方が取得する情報</h2>
<p>当方は、利用者の氏名・メールアドレス・電話番号などを本アプリで取得することはありません。本アプリで扱う写真・画像・入力内容は、原則として利用者の端末内で処理・保存され、当方のサーバーへ送信されることはありません。</p>

<h2>2. 端末の機能へのアクセス</h2>
<ul>
  <li><strong>写真ライブラリ・カメラ</strong>：写真の検索・比較・変換・削除・登録など、各アプリの機能を提供するためにのみ使用します。画像の解析は端末内で行います。</li>
  <li><strong>位置情報</strong>：「参拝記録」で周辺の神社の表示と参拝記録の判定に、「類似写真検索」で撮影場所による絞り込みに使用します。いずれもアプリの使用中のみ利用し、当方へ送信することはありません。</li>
  <li><strong>リマインダー</strong>：「参拝記録」で、授与品の更新時期をお知らせするために使用します。</li>
</ul>
<p>これらのアクセスは、iPhoneの［設定］からいつでも許可・拒否を変更できます。</p>

<h2>3. 広告（Google AdMob）</h2>
<p>本アプリの無料版では、Google LLC が提供する広告配信サービス「Google AdMob」を利用しています。AdMob は、広告の配信・効果測定・不正防止のために、広告識別子（IDFA）、端末情報、おおよその位置情報、広告の表示・操作に関する情報、クラッシュなどの診断情報を取得する場合があります。</p>
<p>IDFA を利用したトラッキングは、iOS の「App Tracking Transparency」の確認画面で利用者が許可した場合にのみ行われます。許可しない場合も広告は表示されますが、パーソナライズされない広告になります。この設定は［設定］＞［プライバシーとセキュリティ］＞［トラッキング］からいつでも変更できます。</p>
<p>Google による情報の取り扱いについては、<a href="https://policies.google.com/technologies/partner-sites?hl=ja" target="_blank" rel="noopener">Google のポリシー</a>をご確認ください。</p>

<h2>4. アプリ内課金（RevenueCat）</h2>
<p>アプリ内課金の購入状態を確認・管理するため、RevenueCat, Inc. のサービスを利用しています。購入履歴と、アプリが発行する匿名の識別子が RevenueCat に送信されます。支払いはAppleが処理し、当方および RevenueCat がクレジットカード情報などを取得することはありません。詳しくは <a href="https://www.revenuecat.com/privacy/" target="_blank" rel="noopener">RevenueCat のプライバシーポリシー</a>をご確認ください。</p>

<h2>5. iCloud・Game Center（参拝記録）</h2>
<ul>
  <li>参拝記録・写真・メモのバックアップは、利用者ご自身のiCloud（CloudKit のプライベートデータベース）に保存されます。当方がその内容を閲覧することはできません。</li>
  <li>神社の情報など、アプリの機能に必要な共有データは CloudKit のパブリックデータベースで管理します。</li>
  <li>ランキングに参加した場合、Game Center のプレイヤー名と参拝数などの集計値が、Game Center 上で他の利用者に表示されます。</li>
</ul>

<h2>6. お問い合わせフォームと本サイトのアクセス解析</h2>
<p>お問い合わせや情報の修正報告には Google フォームを利用しています。入力された内容は、回答と本アプリの改善のためにのみ使用します。</p>
<p>本サイトでは、閲覧状況を把握するために Cloudflare Web Analytics を利用しています。Cookie を使用せず、閲覧したページ、参照元、おおよその地域、ブラウザの種類などを個人を特定しない形で集計します。</p>

<h2>7. 第三者への提供</h2>
<p>上記の外部サービスでの取り扱いを除き、法令に基づく場合を除いて、利用者の情報を本人の同意なく第三者に提供・販売することはありません。</p>

<h2>8. データの削除</h2>
<p>アプリを削除すると、端末内に保存されたデータは削除されます。iCloud に保存したデータは、［設定］＞［Apple アカウント］＞［iCloud］から削除できます。</p>

<h2>9. 改定</h2>
<p>法令の改正や機能の変更に応じて、本ポリシーを改定することがあります。重要な変更はこのページまたはアプリ内でお知らせします。</p>

<h2>10. お問い合わせ窓口</h2>
<p>川助商店（kawasuke store）<br>{form_ja}</p>
"""

    en = f"""
<p>This Privacy Policy explains how Kawasuke Store (川助商店, "we") handles information in the iOS apps we provide ({names_en}; together, the "Apps").</p>
<p class="fine">This English version is provided for convenience. If there is any inconsistency, the Japanese version prevails.</p>

<h2>1. Information we collect</h2>
<p>The Apps do not collect your name, email address or phone number. Photos, images and anything you enter are, as a rule, processed and stored on your device and are not sent to our servers.</p>

<h2>2. Access to device features</h2>
<ul>
  <li><strong>Photo library and camera</strong>: used only to provide each App's features, such as searching, comparing, converting, deleting or adding photos. Image analysis runs on your device.</li>
  <li><strong>Location</strong>: used by Shrine Visit Log to show nearby shrines and confirm visits, and by Similar Photo Search to filter photos by place. Location is used only while the App is in use and is never sent to us.</li>
  <li><strong>Reminders</strong>: used by Shrine Visit Log to remind you when it is time to renew charms and other items.</li>
</ul>
<p>You can change these permissions at any time in the iPhone Settings app.</p>

<h2>3. Advertising (Google AdMob)</h2>
<p>The free versions of the Apps use Google AdMob, an advertising service provided by Google LLC. To serve and measure ads and prevent fraud, AdMob may collect the advertising identifier (IDFA), device information, approximate location, ad interaction data, and diagnostics such as crash data.</p>
<p>Tracking with the IDFA happens only if you allow it in the iOS App Tracking Transparency prompt. If you do not allow it, you will still see ads, but they will not be personalized. You can change this anytime in Settings > Privacy & Security > Tracking.</p>
<p>For how Google handles information, see <a href="https://policies.google.com/technologies/partner-sites" target="_blank" rel="noopener">Google's policies</a>.</p>

<h2>4. In-app purchases (RevenueCat)</h2>
<p>We use RevenueCat, Inc. to verify and manage purchases. Your purchase history and an anonymous identifier generated by the App are sent to RevenueCat. Payments are processed by Apple; neither we nor RevenueCat receive your credit card details. See <a href="https://www.revenuecat.com/privacy/" target="_blank" rel="noopener">RevenueCat's Privacy Policy</a> for details.</p>

<h2>5. iCloud and Game Center (Shrine Visit Log)</h2>
<ul>
  <li>Backups of your visit records, photos and notes are stored in your own iCloud (CloudKit private database). We cannot view their contents.</li>
  <li>Shared data needed for the App to work, such as shrine information, is managed in the CloudKit public database.</li>
  <li>If you join the leaderboards, your Game Center player name and totals such as your visit count are shown to other players on Game Center.</li>
</ul>

<h2>6. Contact form and website analytics</h2>
<p>We use Google Forms for inquiries and correction reports. What you submit is used only to respond to you and improve the Apps.</p>
<p>This website uses Cloudflare Web Analytics to understand how it is viewed. It does not use cookies and aggregates information such as pages viewed, referrer, approximate region and browser type without identifying you.</p>

<h2>7. Sharing with third parties</h2>
<p>Except for the services described above and where required by law, we do not share or sell your information to third parties without your consent.</p>

<h2>8. Deleting your data</h2>
<p>Deleting an App removes the data stored on your device. Data saved to iCloud can be deleted in Settings > Apple Account > iCloud.</p>

<h2>9. Changes</h2>
<p>We may update this policy to reflect changes in law or features. We will announce important changes on this page or in the Apps.</p>

<h2>10. Contact</h2>
<p>Kawasuke Store (川助商店)<br>{form_en}</p>
"""
    legal_page("ja", "privacy.html", "プライバシーポリシー", ja, "privacy")
    legal_page("en", "privacy.html", "Privacy Policy", en, "privacy")


def build_eula():
    form_ja = f'<a href="{CONTACT_FORM}" target="_blank" rel="noopener">お問い合わせフォーム</a>'
    form_en = f'<a href="{CONTACT_FORM}" target="_blank" rel="noopener">contact form</a>'
    ja = f"""
<p>本規約は、川助商店（以下「当方」）が App Store で提供するiOSアプリ（以下「本アプリ」）の利用条件を定めるものです。本アプリには、Apple が定める<a href="{APPLE_EULA}" target="_blank" rel="noopener">標準エンドユーザ使用許諾契約（Licensed Application End User License Agreement）</a>が適用されます。本規約は、それに加えて当方が定める条件です。両者が矛盾する場合は Apple の標準EULAが優先されます。</p>

<div class="apple-eula">
<h2>Apple 標準EULA（Licensed Application End User License Agreement）</h2>
<p>本アプリには、Apple の標準EULAが適用されます。全文（英語）は <a href="{APPLE_EULA}" target="_blank" rel="noopener">Apple のウェブサイト</a>でご確認ください。以下は主な内容の要約です。正式な内容は全文が優先します。</p>
<ol class="eula-summary" type="a">
  <li><strong>使用許諾の範囲</strong>：自分が所有・管理するApple製デバイスで使用できる、譲渡できない権利です。アプリの譲渡・再配布・複製・リバースエンジニアリング・改変はできません。</li>
  <li><strong>データ利用への同意</strong>：アップデートやサポートのため、端末やソフトウェアに関する技術情報が収集される場合があります。個人を特定しない形で、製品の改善に使われます。</li>
  <li><strong>契約の終了</strong>：利用者または提供者が終了するまで有効です。規約に違反した場合、利用の権利は自動的に終了します。</li>
  <li><strong>外部サービス</strong>：アプリから利用する第三者のサービスは、利用者の責任で使用します。その内容や正確性について、提供者は責任を負いません。</li>
  <li><strong>保証の否認</strong>：アプリは「現状のまま」提供され、明示・黙示を問わず保証はありません（法令で認められない地域を除く）。</li>
  <li><strong>責任の制限</strong>：法令で認められる範囲で、提供者は間接的な損害について責任を負わず、損害賠償の総額にも上限が設けられています。</li>
  <li><strong>輸出規制</strong>：米国および各国の輸出関連法令に従って使用するものとします。</li>
  <li><strong>米国政府機関の利用</strong>：米国政府機関には商用品としてライセンスされます。</li>
  <li><strong>準拠法</strong>：原則として米国カリフォルニア州法が適用されます（EU加盟国などの居住者には居住国の法律が適用される場合があります）。</li>
</ol>
</div>

<h2>川助商店の追加条件</h2>
<p>以下は、Apple の標準EULAに加えて当方が定める条件です。両者が矛盾する場合は Apple の標準EULAが優先されます。</p>

<h2>1. 使用許諾</h2>
<p>当方は利用者に対し、利用者が所有または管理するApple製デバイスで、本アプリを個人的・非商用の目的で使用する、譲渡できない非独占的な権利を許諾します。本アプリの著作権その他の権利は当方に帰属します。</p>

<h2>2. 禁止事項</h2>
<ul>
  <li>本アプリの複製、改変、リバースエンジニアリング、再配布</li>
  <li>法令や公序良俗に反する目的での使用、第三者の権利を侵害する使用</li>
  <li>本アプリやサーバーの運営を妨げる行為</li>
</ul>

<h2>3. 有料機能とサブスクリプション</h2>
<ul>
  <li>本アプリには、買い切りの有料機能と、自動更新のサブスクリプションがあります。内容と価格は各アプリの購入画面に表示します。</li>
  <li>支払いは Apple ID に請求されます。サブスクリプションは、期間終了の24時間以上前に解約しない限り、同じ条件で自動的に更新されます。</li>
  <li>解約はiPhoneの［設定］＞［Apple アカウント］＞［サブスクリプション］から行えます。アプリ内からは解約できません。解約後も、期間の終了までは利用できます。</li>
  <li>返金はAppleの規定に従います。当方が直接返金を行うことはできません。</li>
  <li>購入は、同じ Apple ID でサインインしたデバイスで「購入を復元」から引き継げます。</li>
</ul>

<h2>4. 広告</h2>
<p>無料版では第三者が配信する広告を表示します。広告の内容や広告主の商品・サービスは、当方が推奨・保証するものではありません。広告に伴う情報の取り扱いは<a href="privacy.html">プライバシーポリシー</a>に記載しています。</p>

<h2>5. データの保管とバックアップ</h2>
<ol>
  <li>本アプリで作成・保存したデータ（記録・画像・写真など）は、利用者の端末内、または利用者ご自身のiCloudに保存されます。当方はこれらのデータをお預かりしておらず、その永続的な保管や完全性をお約束することはできません。</li>
  <li>端末の故障・紛失、iOSのアップデート、iCloudの不具合、空き容量の不足、誤操作、その他予期しない原因により、データが消失・破損することがあります。大切な写真や画像は、「写真」アプリや外部ストレージなどに、利用者ご自身でも原本を保管してください。写真を削除・変換する機能では、実行前に内容をご確認ください。</li>
  <li>有料プランの終了、その他の機能や利用条件の変更に伴うデータの扱いは、そのつどアプリ内でご案内します。ご案内した内容に沿って行われたデータの変更については、当方は責任を負いかねます。</li>
</ol>

<h2>6. 提供する情報について</h2>
<p>本アプリが表示する換算値、暦・歴史データ、地図や施設の情報、計測値などは正確であるよう努めていますが、その完全性・正確性を保証するものではありません。重要な判断に用いる場合は、公式の情報源もあわせてご確認ください。</p>

<h2>7. 免責と責任の制限</h2>
<ol>
  <li>本アプリは、現状のまま提供されます。特に無料でご利用いただける機能は、特定の目的に適合することや、不具合・中断がないことを保証するものではありません。</li>
  <li>本アプリの利用または利用できなかったこと、データの消失・破損などにより利用者に損害が生じた場合、当方は、利用者に現実に生じた直接かつ通常の損害に限り責任を負い、特別な事情から生じた損害（逸失利益、精神的損害などを含みます）については責任を負いません。</li>
  <li>前項は、当方に故意または重大な過失がある場合には適用しません。</li>
</ol>

<h2>8. 変更・提供の終了</h2>
<p>当方は、本アプリの内容の変更や提供の終了を行うことがあります。本規約を変更する場合は、効力が生じる日とあわせて、このページまたはアプリ内で事前にお知らせします。</p>

<h2>9. 準拠法・管轄</h2>
<p>本追加条件は日本法に準拠します（Apple の標準EULAの準拠法は、同EULAの定めによります）。本追加条件に関して紛争が生じた場合は、当方の所在地を管轄する裁判所を第一審の専属的合意管轄裁判所とします。</p>

<h2>10. お問い合わせ</h2>
<p>川助商店（kawasuke store）<br>{form_ja}</p>

<h2>11. アプリ別の補足</h2>
<p>上記の共通事項に加えて、以下のアプリには次の事項が適用されます。</p>

<h3 id="app-sanpai">参拝記録</h3>
<ol>
  <li>本アプリは、個別の神社、宗教法人その他の団体が運営・公認する公式アプリではありません。</li>
  <li>神社の名称・所在地・祭神などの情報は、OpenStreetMap の公開データをもとに当方が整理したものです（© OpenStreetMap contributors、Open Database License）。実際と異なる場合があるため、参拝できる時間や立ち入れる場所などは、各神社の案内に従ってください。</li>
  <li>参拝の記録は位置情報をもとに判定するため、誤差が生じることがあります。記録の有無は、実際の参拝を証明するものではありません。アプリ内の記録や表示は、御朱印・神札などの授与品に代わるものではありません。</li>
  <li>境内では各神社の定めやマナーに従い、歩きながらの操作は控えてください。撮影が禁止されている場所では撮影しないでください。</li>
  <li>ランキングに参加すると、Game Center の表示名と参拝数などが他の利用者に表示されます。不正な位置情報などによる記録は、除外または訂正することがあります。</li>
  <li>神社情報の更新、重複データの統合、分類の見直しなどのメンテナンスに伴い、登録済みの写真や記録の紐付け先や表示のされ方が変わることがあります。</li>
  <li>氏神設定の変更に伴うデータの扱いは、アプリ内でご案内します。</li>
</ol>

<h3 id="app-photos">類似写真検索・JPEG/HEIF変換</h3>
<ol>
  <li>写真の削除は、iOSの「写真」アプリと同じ仕組みで行われます。削除した写真は「最近削除した項目」に移り、一定期間（通常30日）が過ぎると完全に削除されて元に戻せなくなります。</li>
  <li>類似度の判定は目安です。削除する写真は、実行前にご自身でご確認ください。</li>
  <li>JPEG/HEIF変換で「変換後に元の写真を削除する」設定を有効にしている場合、変換が終わると元の写真は削除されます。変換後の写真は、画質や撮影情報（メタデータ）が元の写真と異なる場合があります。</li>
</ol>

<h3 id="app-fishing">釣り師の単位変換</h3>
<ol>
  <li>換算値、早見表、道糸・ハリスの太さの提案は、一般的な目安です。規格はメーカーや製品によって異なるため、実際の製品の表示を優先してください。</li>
  <li>釣行中の安全確保は、利用者ご自身でお願いします。</li>
</ol>
"""
    en = f"""
<p>These Terms set out the conditions for using the iOS apps that Kawasuke Store (川助商店, "we") provides on the App Store (the "Apps"). Apple's <a href="{APPLE_EULA}" target="_blank" rel="noopener">Licensed Application End User License Agreement</a> (Standard EULA) applies to the Apps. These Terms are additional conditions set by us; if they conflict, Apple's Standard EULA prevails.</p>
<p class="fine">This English version is provided for convenience. If there is any inconsistency, the Japanese version prevails.</p>

<div class="apple-eula">
<h2>Apple Standard EULA (Licensed Application End User License Agreement)</h2>
<p>Apple's Standard EULA applies to the Apps. Please read the full text on <a href="{APPLE_EULA}" target="_blank" rel="noopener">Apple's website</a>. Below is a summary of its main points; the full text always prevails.</p>
<ol class="eula-summary" type="a">
  <li><strong>Scope of license</strong>: a non-transferable right to use the App on Apple devices you own or control. You may not transfer, redistribute, copy, reverse engineer or modify it.</li>
  <li><strong>Consent to use of data</strong>: technical information about your device and software may be collected to provide updates and support, and used to improve products in a form that does not identify you.</li>
  <li><strong>Termination</strong>: the license remains effective until terminated by you or the licensor, and ends automatically if you breach its terms.</li>
  <li><strong>External services</strong>: third-party services used through the App are used at your own risk; the licensor is not responsible for their content or accuracy.</li>
  <li><strong>No warranty</strong>: the App is provided "as is" without warranties of any kind, except where the law does not allow such disclaimers.</li>
  <li><strong>Limitation of liability</strong>: to the extent permitted by law, the licensor is not liable for indirect damages, and total liability is capped.</li>
  <li><strong>Export</strong>: you must comply with U.S. and other applicable export laws.</li>
  <li><strong>U.S. Government end users</strong>: the App is licensed to U.S. Government end users as a commercial item.</li>
  <li><strong>Governing law</strong>: generally the laws of California, U.S.A. (residents of the EU and certain other countries may be governed by the laws of their country of residence).</li>
</ol>
</div>

<h2>Additional terms from Kawasuke Store</h2>
<p>The following are additional terms set by us on top of Apple's Standard EULA. If they conflict, Apple's Standard EULA prevails.</p>

<h2>1. License</h2>
<p>We grant you a non-transferable, non-exclusive right to use the Apps for personal, non-commercial purposes on Apple devices you own or control. All copyrights and other rights in the Apps belong to us.</p>

<h2>2. Prohibited conduct</h2>
<ul>
  <li>Copying, modifying, reverse engineering or redistributing the Apps</li>
  <li>Using the Apps for unlawful purposes or in ways that infringe the rights of others</li>
  <li>Interfering with the Apps or their servers</li>
</ul>

<h2>3. Paid features and subscriptions</h2>
<ul>
  <li>The Apps offer one-time purchases and auto-renewing subscriptions. Details and prices are shown on each App's purchase screen.</li>
  <li>Payment is charged to your Apple ID. Subscriptions renew automatically on the same terms unless cancelled at least 24 hours before the end of the current period.</li>
  <li>Cancel in Settings > Apple Account > Subscriptions; subscriptions cannot be cancelled from within the Apps. You keep access until the end of the current period.</li>
  <li>Refunds are handled under Apple's policies; we cannot issue refunds directly.</li>
  <li>Purchases can be restored with "Restore Purchases" on any device signed in with the same Apple ID.</li>
</ul>

<h2>4. Advertising</h2>
<p>Free versions show ads delivered by third parties. We do not endorse or guarantee the content of ads or the products and services of advertisers. How information is handled for ads is described in our <a href="privacy.html">Privacy Policy</a>.</p>

<h2>5. Storage and backup of your data</h2>
<ol>
  <li>Data you create in the Apps (such as records, images and photos) is stored on your device or in your own iCloud. We do not hold this data and cannot promise that it will be kept permanently or remain intact.</li>
  <li>Data may be lost or damaged through device failure or loss, iOS updates, iCloud problems, lack of storage, user error or other unexpected causes. Please keep your own copies of important photos and images in the Photos app or other storage. Review your selection before using features that delete or convert photos.</li>
  <li>How your data is handled when a paid plan ends, or when other features or terms change, will be explained in the App each time. We are not responsible for changes to your data made in line with those explanations.</li>
</ol>

<h2>6. Information in the Apps</h2>
<p>We strive to keep conversion values, calendar and historical data, map and place information, and measurements accurate, but we do not guarantee that they are complete or correct. Please also check official sources before relying on them for important decisions.</p>

<h2>7. Disclaimer and limitation of liability</h2>
<ol>
  <li>The Apps are provided as is. In particular, features available free of charge are not guaranteed to be fit for any particular purpose or to be free of defects or interruptions.</li>
  <li>If you suffer damage from using or being unable to use the Apps, or from loss or damage of data, we are liable only for direct and ordinary damage actually incurred, and not for damage arising from special circumstances (including lost profits and emotional distress).</li>
  <li>The preceding paragraph does not apply in cases of our willful misconduct or gross negligence.</li>
</ol>

<h2>8. Changes and discontinuation</h2>
<p>We may change or discontinue the Apps. If we change these Terms, we will announce the change and its effective date in advance on this page or in the Apps.</p>

<h2>9. Governing law and jurisdiction</h2>
<p>These additional terms are governed by the laws of Japan (Apple's Standard EULA is governed as stated in that agreement). Any dispute relating to these additional terms shall be subject to the exclusive jurisdiction of the court having jurisdiction over our location as the court of first instance.</p>

<h2>10. Contact</h2>
<p>Kawasuke Store (川助商店)<br>{form_en}</p>

<h2>11. App-specific terms</h2>
<p>In addition to the common terms above, the following apply to these Apps.</p>

<h3 id="app-sanpai">Shrine Visit Log</h3>
<ol>
  <li>This App is not an official app operated or endorsed by any shrine, religious corporation or other organization.</li>
  <li>Shrine names, locations, enshrined deities and other information are compiled by us from public OpenStreetMap data (© OpenStreetMap contributors, Open Database License). Information may differ from reality, so please follow each shrine's guidance on visiting hours and accessible areas.</li>
  <li>Visits are confirmed using location data, which can be inaccurate. A recorded visit is not proof of an actual visit, and nothing in the App replaces goshuin, ofuda or other items received from a shrine.</li>
  <li>On shrine grounds, follow each shrine's rules and etiquette, and avoid using your phone while walking. Do not take photos where photography is prohibited.</li>
  <li>If you join the leaderboards, your Game Center name and totals such as your visit count are shown to other players. Records based on falsified location data or similar may be removed or corrected.</li>
  <li>Maintenance such as updating shrine information, merging duplicate data or revising categories may change which shrine your photos and records are linked to, or how they are displayed.</li>
  <li>How your data is handled when you change your guardian-shrine (ujigami) setting will be explained in the App.</li>
</ol>

<h3 id="app-photos">Similar Photo Search / JPEG/HEIF Converter</h3>
<ol>
  <li>Photos are deleted the same way as in the iOS Photos app: they move to Recently Deleted and are permanently removed after a period of time (usually 30 days), after which they cannot be recovered.</li>
  <li>Similarity scores are a guide only. Please check the photos yourself before deleting them.</li>
  <li>If the JPEG/HEIF Converter setting to delete originals after conversion is on, the original photos are deleted once conversion finishes. Converted photos may differ from the originals in image quality and metadata.</li>
</ol>

<h3 id="app-fishing">Angler's Unit Converter</h3>
<ol>
  <li>Conversion values, reference charts and suggested line and leader sizes are general guides. Standards vary by manufacturer and product, so always follow the actual product labeling.</li>
  <li>Please take responsibility for your own safety while fishing.</li>
</ol>
"""
    legal_page("ja", "eula.html", "利用規約（EULA）", ja, "eula")
    legal_page("en", "eula.html", "Terms of Use (EULA)", en, "eula")


def build_404(lang):
    t = T[lang]
    home = "/index.html" if lang == "ja" else "/en/index.html"  # noqa
    body = f"""
<section class="section">
  <div class="wrap legal center">
    <h1>{t['nf_title']}</h1>
    <p>{t['nf_body']}</p>
    <p><a class="btn btn-primary" href="{home}">{t['nf_home']}</a></p>
  </div>
</section>
"""
    write(lang, "404.html", page(lang, "404.html", t["nf_title"], body, absolute=True))


AI_BOTS = ["GPTBot", "OAI-SearchBot", "ChatGPT-User", "ClaudeBot", "Claude-SearchBot", "Claude-User",
           "PerplexityBot", "Perplexity-User", "Google-Extended", "Applebot-Extended"]


def _url_of(rel):
    """public/ からの相対パス → 公開URL"""
    rel = rel.removesuffix(".html")
    if rel == "index":
        return SITE + "/"
    if rel.endswith("/index"):
        return SITE + "/" + rel.removesuffix("index")
    return SITE + "/" + rel


def build_seo():
    """AIや検索エンジン向けの robots.txt / sitemap.xml / llms.txt"""
    robots = "User-agent: *\nAllow: /\n\n" + "".join(f"User-agent: {b}\nAllow: /\n\n" for b in AI_BOTS)
    robots += f"Sitemap: {SITE}/sitemap.xml\n"
    (OUT / "robots.txt").write_text(robots, encoding="utf-8")

    # 同じ内容の各言語版をまとめて、hreflang の対応関係も書く
    groups = {}
    for f in sorted(OUT.rglob("*.html")):
        rel = f.relative_to(OUT).as_posix()
        if rel.endswith("404.html"):
            continue
        head, _, rest = rel.partition("/")
        lg, key = (head, rest) if head in CONTENT_LANG_ORDER else ("ja", rel)
        groups.setdefault(key, {})[lg] = _url_of(rel)
    rows = []
    for key, urls in groups.items():
        alts = "".join(f'\n    <xhtml:link rel="alternate" hreflang="{lg}" href="{u}"/>' for lg, u in urls.items()) \
            if len(urls) > 1 else ""
        for u in urls.values():
            rows.append(f"  <url>\n    <loc>{u}</loc>{alts}\n  </url>")
    (OUT / "sitemap.xml").write_text(
        '<?xml version="1.0" encoding="UTF-8"?>\n'
        '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9" xmlns:xhtml="http://www.w3.org/1999/xhtml">\n'
        + "\n".join(rows) + "\n</urlset>\n", encoding="utf-8")

    # llms.txt：AI向けに、店と各アプリを短く要約したテキスト
    L = ["# 川助商店 (kawasuke store)", "",
         "> 日本の個人開発者が2013年から作っている、iPhoneアプリの店です。写真の整理・比較、画像形式の変換、和暦の変換、釣りの単位変換などの小さな道具を提供しています。",
         "> A one-person iPhone app shop from Japan, making small tools since 2013: photo sorting and comparison, image format conversion, Japanese calendar conversion, fishing unit conversion and more.",
         "", "## Apps", ""]
    for a in APPS:
        soon = "" if a["id"] else "（近日公開 / coming soon）"
        L.append(f"- [{a['name']['ja']} / {a['name']['en']}]({page_url(a['slug'], 'ja')}){soon}: "
                 f"{a['tagline']['ja']} / {a['tagline']['en']} (English: {page_url(a['slug'], 'en')})")
    for a in APPS:
        for lg in ("ja", "en"):
            d = (a.get("llmo") or {}).get(lg)
            if not d:
                continue
            L += ["", f"## {a['name'][lg]}", "", _plain(d["summary"]), ""]
            L += [f"- {h}: {b}" for h, b, _ in d["needs"]]
            L += [""] + [f"Q. {q}\nA. {ans}\n" for q, ans in d["faq"]]
    L += ["## Other pages", "",
          f"- プライバシーポリシー / Privacy Policy: {SITE}/privacy , {SITE}/en/privacy",
          f"- 利用規約 / Terms of Use (EULA): {SITE}/eula , {SITE}/en/eula",
          f"- お問い合わせ / Contact: {CONTACT_FORM}", ""]
    (OUT / "llms.txt").write_text("\n".join(L), encoding="utf-8")


if __name__ == "__main__":
    for a in APPS:
        a["_content_langs"] = load_content_langs(a)
        load_llmo(a)
    for lang in LANGS:
        build_index(lang)
        for a in APPS:
            build_app(lang, a)
        build_404(lang)
    build_privacy()
    build_eula()
    build_seo()
    print("built:", sorted(str(p.relative_to(OUT)) for p in OUT.rglob("*.html")))
