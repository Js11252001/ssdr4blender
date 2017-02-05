# SSDR4Blender
* <A href="https://github.com/mukailab/ssdr4maya">SSDR4Maya</A>をBlenderへ移植したもの
* 頂点アニメーションをボーンアニメーションに変換するソフト
## 対応環境
* Windows XP以上 (自力でDLLをコンパイルできれば、Mac/Linuxも対応)
* Blender2.65以上 (bl_info書き換えれば2.5.0以上でも動くかも)
* Python3～ (.pydではなく普通のcdeclコールのdllをctypesから呼び出ししてます。Pythonのバージョンが変わっても再コンパイルの必要は無いです)

## インストール方法
* binフォルダにあるビルド済みパッケージ一式を、<A href="https://wiki.blender.org/index.php/Doc:JA/2.6/Manual/Extensions/Python/Add-Ons">Blenderのaddonsフォルダへコピーしてください</A>

## 使用上の注意
* あらかじめ頂点数の変化するModifierを事前にBakeしてください。
* あらかじめCloth/Softbody Physicsを事前にBakeしてください。<A href="http://blender.stackexchange.com/questions/42910/how-to-bake-object-with-cloth-simulation-and-subsurf-not-applied-having-troub">標準でBakeする機能は無いです。.mddを経由してShape-keyアニメーションに変換してください。.mddを読み込んだあと、必ずPhysicsタブから物理演算を無効にしてください（２重効果になります）</A>

###利用手順
1. 処理対象となるシェイプを選択します。
2. メニューの[Object]->[SSDR]より処理を開始します。
3. 処理が終わったら、左下部分でパラメータを調整できます。numMaxIterationsを納得できる最小値に設定してください。頂点数が少なく結果がおかしい場合numMinBonesを減らして見てください。

### 計算パラメータの調整

- numMinBones： 頂点アニメーション近似に用いる最小ボーン数
- numMaxIterations： 最大反復回数
- numMaxInfluences： 各頂点当たりに割り当てられる最大ボーン数

これら3つのパラメータの変更することで、それにともなう計算結果の変化を確認できると思います。現状では、最小ボーン数に大きな値を与えると計算が破綻することを確認しています。

## ビルドと実行方法
* 拡張ライブラリ ssdr.dll は 外部ライブラリとして [Eigen](http://eigen.tuxfamily.org/ "Eigen")、 [QuadProg++](http://quadprog.sourceforge.net/ "QuadProg++")が必要です。
* EigenはCMakeする必要はありません！（とんでもなくめちゃくちゃ時間がかかります。コンパイルする必要はありません。Includeフォルダに設定するだけで良いです）
* QuadProg++.cc、727行あたりのvoid cholesky_decomposition(Matrix<double>& A)関数の、throw～、exit(-1);の2行をコメントアウトしてください


###ビルド手順

1. Eigenのインストールフォルダにインクルードパスを通す。
4. QuadProg++をダウンロードし、下記4つのファイルをssdrフォルダにコピーする。
 * QuadProg++.hh
 * QuadProg++.cc
 * Array.hh
 * Array.cc
5. Visual Studio 上でビルド＆実行
